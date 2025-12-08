from .base import BaseProvider
from typing import List, Dict


class Google(BaseProvider):
    v2fly_company: str = "google"
    # domains = ["googleapis.cn", "googleapis.com", "cloud.google.com", "gcp.gvt2.com", "appspot.com", "firebaseio.com", "google"]
    tags: List[str] = ["cloud"]
    org_ids: List[str] = []
    _bucket_name_regex = r"[a-z0-9][a-z0-9-_\.]{1,61}[a-z0-9]"
    _firebase_bucket_name_regex = r"[a-z0-9][a-z0-9-\.]{1,61}[a-z0-9]"
    regexes: Dict[str, List[str]] = {
        "STORAGE_BUCKET_NAME": [_bucket_name_regex, _firebase_bucket_name_regex],
        "STORAGE_BUCKET_HOSTNAME": [
            r"(" + _firebase_bucket_name_regex + r")\.(firebaseio\.com)",
            r"(" + _bucket_name_regex + r")\.(storage\.googleapis\.com)",
        ]
    }

    _ips_url = "https://www.gstatic.com/ipranges/cloud.json"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        for p in response.json()["prefixes"]:
            try:
                ranges.add(p["ipv4Prefix"])
            except KeyError:
                ranges.add(p["ipv6Prefix"])
        return list(ranges)

