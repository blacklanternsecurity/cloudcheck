from cloudcheck.providers.base import BaseProvider
from typing import List


class Wasabi(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "Wasabi"
    long_description: str = "A cloud storage provider offering hot cloud storage services with high performance and low cost."
    # {"org_id": "BLUEA-2-ARIN", "org_name": "Wasabi Technologies, Inc.", "country": "US", "asns": [395717]}
    # {"org_id": "ORG-WTI2-AP-APNIC", "org_name": "Wasabi Technologies Inc.", "country": "US", "asns": [140642]}
    org_ids: List[str] = [
        "BLUEA-2-ARIN",
        "ORG-WTI2-AP-APNIC",
    ]
    domains: List[str] = [
        "wasabi.com",
    ]
