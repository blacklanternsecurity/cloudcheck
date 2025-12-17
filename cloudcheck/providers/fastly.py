from cloudcheck.providers.base import BaseProvider
from typing import List


class Fastly(BaseProvider):
    v2fly_company: str = "fastly"
    tags: List[str] = ["cdn"]
    # {"org_id": "SKYCA-3-ARIN", "org_name": "Fastly, Inc.", "country": "US", "asns": [895,54113,394192]}
    org_ids: List[str] = [
        "SKYCA-3-ARIN",
    ]

    _ips_url = "https://api.fastly.com/public-ip-list"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        j = response.json()
        if j and isinstance(j, dict):
            addresses = j.get("addresses", [])
            if addresses and isinstance(addresses, list):
                return list(set(addresses))
        return []
