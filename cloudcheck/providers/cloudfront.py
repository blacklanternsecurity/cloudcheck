from .base import BaseProvider
from typing import List, Dict


class Cloudfront(BaseProvider):
    v2fly_company: str = ""
    # domains = ["cloudfront.com", "cloudfront.net"]
    tags: List[str] = ["cdn"]
    org_ids: List[str] = []

    _ips_url = "https://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        response_json = response.json()
        if not isinstance(response_json, dict):
            raise ValueError(f"Invalid response format: {type(response_json)}")
        for r in response_json.values():
            ranges.update(r)
        return list(ranges)

