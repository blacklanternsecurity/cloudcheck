from cloudcheck.providers.base import BaseProvider
from typing import List


class Cdnetworks(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "CDNetworks (씨디네트웍스)"
    long_description: str = (
        "A Korean content delivery network provider offering CDN and cloud services."
    )
    # {"org_id": "CDNET-ARIN", "org_name": "CDNetworks Inc.", "country": "US", "asns": [36408,40366]}
    org_ids: List[str] = [
        "CDNET-ARIN",
    ]
