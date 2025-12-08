from .base import BaseProvider
from typing import List, Dict


class Imperva(BaseProvider):
    v2fly_company: str = ""
    # domains = ["imperva.com"]
    # asns = [62571]
    tags: List[str] = ["cdn"]
    org_ids: List[str] = []

    _ips_url = "https://my.imperva.com/api/integration/v1/ips"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        data = response.json()
        for ipv4 in data.get("ipRanges", []):
            ranges.add(ipv4)
        for ipv6 in data.get("ipv6Ranges", []):
            ranges.add(ipv6)
        return list(ranges)

