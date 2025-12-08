from .base import BaseProvider
from typing import List, Dict


class Oracle(BaseProvider):
    v2fly_company: str = "oracle"
    # domains = ["oracle", "oracle.com", "oraclecloud.com", "oraclefoundation.org", "oracleimg.com", "oracleinfinity.io", "ateam-oracle.com", "sun.com"]
    tags: List[str] = ["cloud"]
    org_ids: List[str] = []

    _ips_url = "https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        for region in response.json()["regions"]:
            for cidr in region["cidrs"]:
                ranges.add(cidr["cidr"])
        return list(ranges)

