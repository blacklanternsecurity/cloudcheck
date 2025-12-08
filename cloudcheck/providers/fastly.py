from .base import BaseProvider
from typing import List, Dict


class Fastly(BaseProvider):
    v2fly_company: str = "fastly"
    # domains = ["fastly.com", "fastly.net", "fastlylabs.com", "fastlylb.net", "fastly-terrarium.com", "zencdn.net"]
    tags: List[str] = ["cdn"]
    org_ids: List[str] = []

    _ips_url = "https://api.fastly.com/public-ip-list"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        j = response.json()
        if j and isinstance(j, dict):
            addresses = j.get("addresses", [])
            if addresses and isinstance(addresses, list):
                return list(set(addresses))
        return []

