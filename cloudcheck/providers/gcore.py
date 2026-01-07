from cloudcheck.providers.base import BaseProvider
from typing import List


class Gcore(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "G-Core Labs"
    long_description: str = "A content delivery network and cloud infrastructure provider offering CDN, cloud computing, and edge services."
    # {"org_id": "ORG-GLS1-AP-APNIC", "org_name": "G-Core Labs S.A", "country": "LU", "asns": [59245]}
    # {"org_id": "ORG-WIG6-RIPE", "org_name": "G-Core Labs S.A.", "country": "LU", "asns": [199524,202422,210559]}
    org_ids: List[str] = [
        "ORG-GLS1-AP-APNIC",
        "ORG-WIG6-RIPE",
    ]

    _ips_url = "https://api.gcore.com/cdn/public-ip-list"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        if getattr(response, "status_code", 0) == 200:
            response_json = response.json()
            if isinstance(response_json, dict):
                for key in "addresses", "addresses_v6":
                    for ip_range in response_json.get(key, []):
                        ranges.add(ip_range)
        return list(ranges)
