from cloudcheck.providers.base import BaseProvider
from typing import List


class Iboss(BaseProvider):
    tags: List[str] = ["security"]
    short_description: str = "iboss"
    long_description: str = "A cloud security company providing secure web gateway, CASB, and zero trust network access services."
    org_ids: List[str] = [
        "IBOSS-8-ARIN",  # iboss,inc, US
        "ORG-IA23-AP-APNIC",  # IBOSS Inc., US
        "ORG-II158-RIPE",  # IBOSS, INC, US
    ]
