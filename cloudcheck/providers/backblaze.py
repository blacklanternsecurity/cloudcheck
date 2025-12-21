from cloudcheck.providers.base import BaseProvider
from typing import List


class Backblaze(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "Backblaze"
    long_description: str = "A cloud storage and backup service provider offering data backup and cloud storage solutions."
    # {"org_id": "BACKB-7-ARIN", "org_name": "Backblaze Inc", "country": "US", "asns": [40401,396865]}
    org_ids: List[str] = [
        "BACKB-7-ARIN",
    ]
    domains: List[str] = ["backblaze.com", "backblazeb2.com"]
