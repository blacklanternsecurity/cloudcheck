from cloudcheck.providers.base import BaseProvider
from typing import List


class OVH(BaseProvider):
    tags: List[str] = ["cloud"]
    # {"org_id": "ORG-OS3-RIPE", "org_name": "OVH SAS", "country": "FR", "asns": [16276,35540]}
    org_ids: List[str] = [
        "ORG-OS3-RIPE",
    ]
    domains: List[str] = [
        "ovh",
        "ovh.com",
        "ovhcloud.com",
    ]
