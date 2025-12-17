from cloudcheck.providers.base import BaseProvider
from typing import List, Dict


class Cloudflare(BaseProvider):
    v2fly_company: str = "cloudflare"
    tags: List[str] = ["cdn"]
    # {"org_id": "CLOUD14-ARIN", "org_name": "Cloudflare, Inc.", "country": "US", "asns": [13335,14789,394536,395747,400095]}
    # {"org_id": "ORG-CHKL1-AP-APNIC", "org_name": "Cloudflare Hong Kong, LLC", "country": "US", "asns": [133877]}
    # {"org_id": "ORG-CI4-AP-APNIC", "org_name": "Cloudflare, Inc.", "country": "US", "asns": [132892]}
    # {"org_id": "ORG-CI40-RIPE", "org_name": "Cloudflare Inc", "country": "US", "asns": [202623,203898]}
    # {"org_id": "ORG-CLL6-RIPE", "org_name": "Cloudflare London, LLC", "country": "US", "asns": [209242]}
    # {"org_id": "ORG-CSL5-AP-APNIC", "org_name": "Cloudflare Sydney, LLC", "country": "US", "asns": [139242]}
    org_ids: List[str] = [
        "CLOUD14-ARIN",
        "ORG-CHKL1-AP-APNIC",
        "ORG-CI4-AP-APNIC",
        "ORG-CI40-RIPE",
        "ORG-CLL6-RIPE",
        "ORG-CSL5-AP-APNIC",
    ]
    _bucket_name_regex = r"[a-z0-9_][a-z0-9-\.]{1,61}[a-z0-9]"
    regexes: Dict[str, List[str]] = {
        "STORAGE_BUCKET_NAME": [_bucket_name_regex],
        "STORAGE_BUCKET_HOSTNAME": [
            r"(" + _bucket_name_regex + r")\.(r2\.dev)",
            r"(" + _bucket_name_regex + r")\.(r2\.cloudflarestorage\.com)",
        ],
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
