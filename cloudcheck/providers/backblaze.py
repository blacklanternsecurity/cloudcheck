from cloudcheck.providers.base import BaseProvider
from typing import List


class Backblaze(BaseProvider):
    tags: List[str] = ["cloud"]
    # {"org_id": "BACKB-7-ARIN", "org_name": "Backblaze Inc", "country": "US", "asns": [40401,396865]}
    org_ids: List[str] = [
        "BACKB-7-ARIN",
    ]
    domains: List[str] = ["backblaze.com", "backblazeb2.com"]
