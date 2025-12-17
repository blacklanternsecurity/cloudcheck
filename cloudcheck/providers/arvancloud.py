from cloudcheck.providers.base import BaseProvider
from typing import List


class Arvancloud(BaseProvider):
    domains: List[str] = ["arvancloud.ir"]
    tags: List[str] = ["cdn"]
    # {"org_id": "ORG-AGTL2-RIPE", "org_name": "ARVANCLOUD GLOBAL TECHNOLOGIES L.L.C", "country": "AE", "asns": [57568,208006,210296]}
    org_ids: List[str] = [
        "ORG-AGTL2-RIPE",
    ]

    _ips_url = "https://www.arvancloud.ir/en/ips.txt"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        if getattr(response, "status_code", 0) == 200:
            ranges.update(response.text.splitlines())
        return list(ranges)
