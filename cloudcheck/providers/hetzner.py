from .base import BaseProvider
from typing import List, Dict


class Hetzner(BaseProvider):
    v2fly_company: str = ""
    # domains = ["hetzner.de", "hetzner.com", "hetzner.cloude", "your-server.de", "your-objectstorage.com"]
    # asns = [24940, 212317, 213230, 215859]
    tags: List[str] = ["cloud"]
    org_ids: List[str] = []
    _bucket_name_regex = r"[a-z0-9][a-z0-9-_\.]{1,61}[a-z0-9]"
    regexes: Dict[str, List[str]] = {
        "STORAGE_BUCKET_NAME": [_bucket_name_regex],
        "STORAGE_BUCKET_HOSTNAME": [r"(" + _bucket_name_regex + r")\.(your-objectstorage\.com)"]
    }

