import re
import httpx
import pyasn
import logging
import ipaddress
import traceback
from datetime import datetime
from typing import Dict, List, Union
from pydantic import BaseModel, field_validator

from ..cidr import CidrRanges
from ..helpers import domain_parents

log = logging.getLogger("cloudcheck.providers")


try:
    asndb = pyasn.pyasn("asn.db")
except Exception:
    asndb = None


class CloudProviderJSON(BaseModel):
    name: str = ""
    domains: List[str] = []
    cidrs: List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]] = []
    last_updated: datetime = datetime.min
    bucket_name_regex: str = ""
    regexes: Dict[str, List[str]] = {}
    provider_type: str = "cloud"
    ips_url: str = ""
    asns: List[int] = []

    @field_validator("cidrs")
    @classmethod
    def validate_cidrs(cls, value):
        return [ipaddress.ip_network(v, strict=False) for v in value]


class BaseCloudProvider:
    domains = []
    bucket_name_regex = ""
    regexes = {}
    provider_type = "cloud"
    ips_url = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36"
    }
    asns = []

    def __init__(self, j, httpx_client=None):
        self._httpx_client = httpx_client
        self._log = None
        self.ranges = CidrRanges()
        if j is not None:
            p = CloudProviderJSON(**j)
            self.domains = set(
                [d.lower() for d in set(list(self.domains) + list(p.domains))]
            )
            self.ranges.update(p.cidrs)
            self.last_updated = p.last_updated

        self._bucket_name_regex = re.compile("^" + self.bucket_name_regex + "$", re.I)

        self.signatures = {}
        self.domain_regexes = {}
        for domain in self.domains:
            self.domain_regexes[domain] = re.compile(
                r"^(?:[\w\-]+\.)*" + rf"{re.escape(domain)}$"
            )
        for data_type, regexes in self.regexes.items():
            self.signatures[data_type] = [re.compile(r, re.I) for r in regexes]

    async def update(self):
        try:
            self.last_updated = datetime.now()
            self.ranges = CidrRanges(self.get_subnets())
            if self.ips_url:
                response = await self.httpx_client.get(
                    self.ips_url, follow_redirects=True, headers=self.headers
                )
                ranges = self.parse_response(response)
                if ranges:
                    self.ranges.update(ranges)
        except Exception as e:
            log.warning(f"Error retrieving {self.ips_url}: {e}")
            log.warning(traceback.format_exc())

    def get_subnets(self):
        subnets = set()
        if asndb is not None:
            for asn in self.asns:
                prefixes = asndb.get_as_prefixes(asn)
                if prefixes:
                    for subnet in prefixes:
                        subnets.add(ipaddress.ip_network(subnet, strict=False))
        return subnets

    def to_json(self):
        """
        domains: List[str] = []
        cidrs: List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]] = []
        last_updated: datetime = datetime.now()
        bucket_name_regex: str = ""
        regexes: Dict[str, List[str]] = {}
        provider_type: str = "cloud"
        ips_url: str = ""
        """
        return CloudProviderJSON(
            name=self.name,
            domains=sorted(self.domains),
            cidrs=sorted([str(r) for r in self.ranges]),
            last_updated=self.last_updated,
            regexes=self.regexes,
            provider_type=self.provider_type,
            ips_url=self.ips_url,
            asns=self.asns,
            bucket_name_regex=self.bucket_name_regex,
        ).dict()

    @property
    def httpx_client(self):
        if self._httpx_client is None:
            self._httpx_client = httpx.AsyncClient(verify=False)
        return self._httpx_client

    def parse_response(self, response):
        pass

    @classmethod
    @property
    def name(cls):
        return cls.__name__

    @property
    def log(self):
        if self._log is None:
            self._log = logging.getLogger(f"cloudcheck.providers.{self.name.lower()}")
        return self._log

    def is_valid_bucket_name(self, bucket_name):
        return self._bucket_name_regex.match(bucket_name)

    def domain_match(self, s):
        for domain_parent in domain_parents(s):
            if domain_parent in self.domains:
                return domain_parent
        return False

    def __str__(self):
        return self.name

    def __contains__(self, ip):
        return ip in self.ranges
