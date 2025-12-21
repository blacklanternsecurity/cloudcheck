from cloudcheck.providers.base import BaseProvider
from typing import List


class Stormwall(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "StormWall"
    long_description: str = (
        "A DDoS protection and web application firewall service provider."
    )
    # {"org_id": "ORG-SS933-RIPE", "org_name": "StormWall s.r.o.", "country": "SK", "asns": [51558,59796]}
    org_ids: List[str] = [
        "ORG-SS933-RIPE",
    ]
