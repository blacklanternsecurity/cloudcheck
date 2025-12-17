from cloudcheck.providers.base import BaseProvider
from typing import List


class Kamatera(BaseProvider):
    tags: List[str] = ["cloud"]
    # {"org_id": "KAMAT-ARIN", "org_name": "Kamatera, Inc.", "country": "US", "asns": [36007,54913,396948,396949]}
    # {"org_id": "ORG-KI35-RIPE", "org_name": "Kamatera Inc", "country": "US", "asns": [41436,204548,210329,215728]}
    # {"org_id": "ORG-KI4-AP-APNIC", "org_name": "Kamatera, Inc.", "country": "US", "asns": [64022]}
    org_ids: List[str] = [
        "KAMAT-ARIN",
        "ORG-KI35-RIPE",
        "ORG-KI4-AP-APNIC",
    ]
    domains: List[str] = [
        "kamatera.com",
    ]
