from cloudcheck.providers.base import BaseProvider
from typing import List


class Imperva(BaseProvider):
    v2fly_company: str = ""
    domains: List[str] = ["imperva.com"]
    tags: List[str] = ["waf"]
    # {"org_id": "IMPER-62-ARIN", "org_name": "IMPERVA INC", "country": "US", "asns": [62571]}
    org_ids: List[str] = [
        "IMPER-62-ARIN",
    ]

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
