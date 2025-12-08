import ipaddress
from .base import BaseProvider
from typing import List, Dict


class GitHub(BaseProvider):
    v2fly_company: str = "github"
    # domains = ["github.com"]
    tags: List[str] = ["cdn"]
    org_ids: List[str] = []

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

