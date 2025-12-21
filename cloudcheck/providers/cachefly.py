from cloudcheck.providers.base import BaseProvider
from typing import List


class Cachefly(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "CacheFly"
    long_description: str = (
        "A content delivery network provider offering global CDN services."
    )
    # {"org_id": "CL-1923-ARIN", "org_name": "CacheFly", "country": "US", "asns": [30081]}
    org_ids: List[str] = [
        "CL-1923-ARIN",
    ]

    _ips_url = "https://cachefly.cachefly.net/ips/rproxy.txt"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        if getattr(response, "status_code", 0) == 200:
            for line in response.text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    ranges.add(line)
        return list(ranges)
