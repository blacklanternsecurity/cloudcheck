import ipaddress
import os
import traceback
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Union
from pydantic import BaseModel, field_validator, computed_field

from ..helpers import defrag_cidrs, parse_v2fly_domain_file, request


v2fly_repo_pulled = False


class BaseProvider(BaseModel):
    """
    Base class for all cloud providers.

    Each provider inherits from this class and overrides any of the default values.
    They can also override the update_cidrs() method to fetch cidrs from a different source.
    """

    # these values are static and always loaded from the class definition
    regexes: Dict[str, List[str]] = {}
    tags: List[str] = []  # Tags for the provider (e.g. "cdn", "waf", etc.)
    org_ids: List[str] = []  # ASN Organization IDs (e.g. GOGL-ARIN)
    v2fly_company: str = ""  # Company name for v2fly domain fetching

    # these values are dynamic and set by the update() method
    last_updated: float = time.time()

    # these we allow static values but they are later merged with dynamic values
    asns: List[int] = []
    cidrs: List[str] = []
    domains: List[str] = []

    @field_validator("cidrs")
    @classmethod
    def validate_cidrs(cls, value):
        ips = []
        for v in value:
            try:
                ips.append(ipaddress.ip_network(v, strict=False))
            except ValueError:
                print(f"Invalid CIDR: from {cls.__name__}: {v}")
                continue
        ips = [str(ip) for ip in defrag_cidrs(ips)]
        return sorted(ips)

    @field_validator("domains")
    @classmethod
    def validate_domains(cls, value):
        return sorted(list(set([d.lower().strip(".") for d in value])))

    @computed_field(return_type=str)
    @property
    def name(self):
        return self.__class__.__name__

    def __init__(self, **data):
        super().__init__(**data)
        self._cidrs = []
        self._cache_dir = Path.home() / ".cache" / "cloudcheck"
        self._repo_url = "https://github.com/v2fly/domain-list-community.git"
        self._asndb_url = os.getenv("ASNDB_URL", "https://asndb.api.bbot.io/v1")
        self._bbot_io_api_key = os.getenv("BBOT_IO_API_KEY")

    def update(self):
        print(f"Updating {self.name}")
        errors = []
        errors.extend(self.update_domains())
        errors.extend(self.update_cidrs())
        return errors

    def update_domains(self):
        # update dynamic domains
        errors = []
        if self.v2fly_company:
            domains, errors = self.fetch_v2fly_domains()
            if domains:
                self.domains = sorted(list(set(self.domains + domains)))
            else:
                errors.append(
                    f"No v2fly domains were found for {self.name} (company name: {self.v2fly_company})"
                )
        return errors

    def update_cidrs(self):
        cidrs = set()
        errors = []

        # query by direct ASNs
        if self.asns:
            _cidrs, _errors = self.fetch_asns()
            print(f"Got {len(_cidrs)} ASN cidrs for {self.name}'s ASNs {self.asns}")
            if not _cidrs:
                errors.append(
                    f"No ASN cidrs were found for {self.name}'s ASNs {self.asns}"
                )
            errors.extend(_errors)
            cidrs.update(_cidrs)

        # query by org IDs
        if self.org_ids:
            _cidrs, _asns, _errors = self.fetch_org_ids()
            _asns = _asns.copy()
            _asns.update(self.asns)
            self.asns = list(sorted(_asns))
            print(
                f"Got {len(_cidrs)} org id cidrs for {self.name}'s org ids {self.org_ids}"
            )
            if not _cidrs:
                errors.append(
                    f"No cidrs were found for {self.name}'s org ids {self.org_ids}"
                )
            errors.extend(_errors)
            cidrs.update(_cidrs)

        # fetch any dynamically-updated lists of CIDRs
        try:
            dynamic_cidrs = self.fetch_cidrs()
            print(f"Got {len(dynamic_cidrs)} dynamic cidrs for {self.name}")
            cidrs.update(dynamic_cidrs)
        except Exception as e:
            errors.append(
                f"Failed to fetch dynamic cidrs for {self.name}: {e}:\n{traceback.format_exc()}"
            )

        # finally, put in any manually-specified CIDRs
        print(f"Adding {len(self.cidrs)} manually-specified cidrs for {self.name}")
        if self.cidrs:
            cidrs.update(self.cidrs)

        print(f"Total {len(cidrs)} cidrs for {self.name}")

        try:
            self.cidrs = self.validate_cidrs(cidrs)
        except Exception as e:
            errors.append(
                f"Error validating ASN cidrs for {self.name}: {e}:\n{traceback.format_exc()}"
            )

        self.last_updated = time.time()

        return errors

    def fetch_org_ids(
        self,
    ) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
        """Takes org_ids and populates the .asns and .cidrs attributes."""
        errors = []
        cidrs = set()
        print(f"Fetching {len(self.org_ids)} org ids for {self.name}")
        asns = set()
        for org_id in self.org_ids:
            print(f"Fetching cidrs for {org_id} from asndb")
            try:
                url = f"{self._asndb_url}/org/{org_id}"
                print(f"Fetching {url}")
                res = self.request(url, include_api_key=True)
                print(f"{url} -> {res}: {res.text}")
                j = res.json()
            except Exception as e:
                errors.append(
                    f"Failed to fetch cidrs for {org_id} from asndb: {e}:\n{traceback.format_exc()}"
                )
                continue
            _asns = j.get("asns", [])
            for asn in _asns:
                asns.add(asn)
                asn_cidrs, _errors = self.fetch_asn(asn)
                errors.extend(_errors)
                cidrs.update(asn_cidrs)
        return cidrs, asns, errors

    def fetch_asns(self) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
        """Fetch CIDRs for a given list of ASNs from ASNDB."""
        cidrs = []
        errors = []
        print(f"Fetching {len(self.asns)} ASNs for {self.name}")
        for asn in self.asns:
            asn_cidrs, _errors = self.fetch_asn(asn)
            errors.extend(_errors)
            cidrs.update(asn_cidrs)
        return cidrs, errors

    def fetch_asn(
        self, asn: int
    ) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
        """Fetch CIDRs for a given ASN from ASNDB."""
        cidrs = []
        errors = []
        url = f"{self._asndb_url}/asn/{asn}"
        print(f"Fetching {url}")
        try:
            res = self.request(url, include_api_key=True)
            print(f"{url} -> {res.text}")
            j = res.json()
            cidrs = j.get("subnets", [])
        except Exception as e:
            errors.append(
                f"Failed to fetch cidrs for {asn} from asndb: {e}:\n{traceback.format_exc()}"
            )
        print(f"Got {len(cidrs)} cidrs for {asn}")
        return cidrs, errors

    def fetch_v2fly_domains(self) -> List[str]:
        """Fetch domains from the v2fly community repository."""
        if not self.v2fly_company:
            return [], []

        errors = []
        repo_path, _success = self._ensure_v2fly_repo_cached()
        company_file = repo_path / "data" / self.v2fly_company
        try:
            domains = parse_v2fly_domain_file(company_file)
        except Exception as e:
            errors.append(
                f"Failed to parse {self.v2fly_company} domains: {e}:\n{traceback.format_exc()}"
            )
        return sorted(list(domains)), errors

    def fetch_cidrs(self) -> List[str]:
        """Fetch CIDRs from a custom source."""
        return []

    def fetch_domains(self) -> List[str]:
        """Fetch domains from a custom source."""
        return []

    def _ensure_v2fly_repo_cached(self) -> Path:
        """Ensure the community repo is cloned and up-to-date."""
        global v2fly_repo_pulled
        errors = []
        repo_dir = self._cache_dir / "domain-list-community"
        if not repo_dir.exists():
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", self._repo_url, str(repo_dir)],
                    check=True,
                    capture_output=True,
                )
                v2fly_repo_pulled = True
            except subprocess.CalledProcessError as e:
                errors.append(
                    f"Failed to clone v2fly repo: {e}:\n{traceback.format_exc()}"
                )
        elif not v2fly_repo_pulled:
            try:
                subprocess.run(
                    ["git", "pull"], cwd=repo_dir, check=True, capture_output=True
                )
            except subprocess.CalledProcessError as e:
                errors.append(
                    f"Failed to pull v2fly repo: {e}:\n{traceback.format_exc()}"
                )
        return repo_dir, errors

    def request(self, *args, **kwargs):
        return request(*args, **kwargs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"
