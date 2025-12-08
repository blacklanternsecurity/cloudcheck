from .base import BaseProvider
from typing import List, Dict


class Arvancloud(BaseProvider):
    v2fly_company: str = ""
    # domains = ["arvancloud.ir"]
    # asns = [57568, 205585, 208006, 210296]
    tags: List[str] = ["cdn"]
    org_ids: List[str] = []

    _ips_url = "https://www.arvancloud.ir/en/ips.txt"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        if getattr(response, "status_code", 0) == 200:
            ranges.update(response.text.splitlines())
        return list(ranges)

