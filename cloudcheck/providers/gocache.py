from cloudcheck.providers.base import BaseProvider
from typing import List


class Gocache(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "GoCache"
    long_description: str = "A Brazilian content delivery network provider offering CDN services."

    _ips_url = "https://gocache.com.br/ips"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        if getattr(response, "status_code", 0) == 200:
            ranges.update(response.text.splitlines())
        return list(ranges)
