from cloudcheck.providers.base import BaseProvider
from typing import List


class X4b(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "X4B"
    long_description: str = (
        "A DDoS protection and content delivery network service provider."
    )
    # {"org_id": "ORG-XA1-AP-APNIC", "org_name": "X4B", "country": "AU", "asns": [136165]}
    org_ids: List[str] = [
        "ORG-XA1-AP-APNIC",
    ]
