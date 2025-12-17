import ipaddress
from cloudcheck.providers.base import BaseProvider
from typing import List


class GitHub(BaseProvider):
    v2fly_company: str = "github"
    tags: List[str] = ["cdn"]
    # {"org_id": "GITHU-ARIN", "org_name": "GitHub, Inc.", "country": "US", "asns": [36459]}
    org_ids: List[str] = [
        "GITHU-ARIN",
    ]

    _ips_url = "https://api.github.com/meta"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        response_json = response.json()
        for k, v in response_json.items():
            if isinstance(v, list):
                for n in v:
                    try:
                        ipaddress.ip_network(n)
                        ranges.add(n)
                    except ValueError:
                        pass
        return list(ranges)
