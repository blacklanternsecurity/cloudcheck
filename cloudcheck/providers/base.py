import httpx
import logging
import ipaddress
import traceback
import regex as re
from datetime import datetime
from radixtarget import RadixTarget
from typing import Dict, List, Union
from pydantic import BaseModel, field_validator

from ..helpers import make_ip_type

log = logging.getLogger("cloudcheck.providers")


asndb = None


base_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


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
    asns = []

    def __init__(self, j):
        self._log = None
        self.ranges = set()
        self.radix = RadixTarget()
        if j is not None:
            p = CloudProviderJSON(**j)
            self.update_domains(
                [d.lower() for d in set(list(self.domains) + list(p.domains))]
            )
            self.update_ranges(p.cidrs)
            self.last_updated = p.last_updated

        self._bucket_name_regex = re.compile("^" + self.bucket_name_regex + "$", re.I)

        self.signatures = {}
        for data_type, regexes in self.regexes.items():
            self.signatures[data_type] = [re.compile(r, re.I) for r in regexes]

    def check(self, host):
        return self.radix.search(host)

    async def update(self):
        try:
            import pyasn
        except ModuleNotFoundError:
            log.warning("Please install pyasn")
            import os

            os._exit(1)

        global asndb
        asndb = pyasn.pyasn("asn.db")
        try:
            self.last_updated = datetime.now()
            self.ranges = self.get_subnets()
            if self.ips_url:
                async with httpx.AsyncClient(
                    transport=httpx.AsyncHTTPTransport(verify=False)
                ) as client:
                    response = await client.get(
                        self.ips_url,
                        follow_redirects=True,
                        headers=base_headers,
                    )
                    ranges = self.parse_response(response)
                    if ranges:
                        self.update_ranges(ranges)
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

    def update_ranges(self, ranges):
        for r in ranges:
            r = make_ip_type(r)
            self.ranges.add(r)
            self.radix.insert(r)

    def update_domains(self, domains):
        for d in domains:
            self.radix.insert(d)

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
        ).model_dump()

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

    def __str__(self):
        return self.name

    def __contains__(self, ip):
        return ip in self.ranges
