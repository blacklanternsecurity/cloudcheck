from .base import BaseProvider
from typing import List, Dict


class Cloudflare(BaseProvider):
    v2fly_company: str = "cloudflare"
    # asns = [13335, 394536, 395747, 14789]
    tags: List[str] = ["cdn"]
    org_ids: List[str] = []
    _bucket_name_regex = r"[a-z0-9_][a-z0-9-\.]{1,61}[a-z0-9]"
    regexes: Dict[str, List[str]] = {
        "STORAGE_BUCKET_NAME": [_bucket_name_regex],
        "STORAGE_BUCKET_HOSTNAME": [
            r"(" + _bucket_name_regex + r")\.(r2\.dev)",
            r"(" + _bucket_name_regex + r")\.(r2\.cloudflarestorage\.com)",
        ]
    }

    _ips_url = "https://api.cloudflare.com/client/v4/ips"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        response_json = response.json()
        for ip_type in ("ipv4_cidrs", "ipv6_cidrs"):
            for ip_range in response_json.get("result", {}).get(ip_type, []):
                ranges.add(ip_range)
        return list(ranges)

