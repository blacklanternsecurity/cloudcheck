from cloudcheck.providers.base import BaseProvider
from typing import List


class DDoSGuard(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "DDoS Guard"
    long_description: str = (
        "A DDoS protection and content delivery network service provider."
    )
    # {"org_id": "ORG-DL236-RIPE", "org_name": "DDOS-GUARD LTD", "country": "RU", "asns": [44556,49612,57724]}
    org_ids: List[str] = [
        "ORG-DL236-RIPE",
    ]
