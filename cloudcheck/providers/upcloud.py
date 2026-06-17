from cloudcheck.providers.base import BaseProvider
from typing import List


class Upcloud(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "UpCloud"
    long_description: str = "A Finnish cloud infrastructure provider offering high-performance cloud servers."
    # {"org_id": "ORG-UL87-RIPE", "org_name": "UpCloud Ltd", "country": "FI", "asns": [202053]}
    # {"org_id": "UU-7-ARIN", "org_name": "UpCloud USA Inc", "country": "US", "asns": [25697]}
    asns: List[int] = [202053, 25697]
    org_ids: List[str] = [
        "ORG-UL87-RIPE",
        "UU-7-ARIN",
    ]
