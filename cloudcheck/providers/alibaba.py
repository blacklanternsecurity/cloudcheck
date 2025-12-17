from cloudcheck.providers.base import BaseProvider
from typing import List


class Alibaba(BaseProvider):
    v2fly_company: str = "alibaba"
    tags: List[str] = ["cloud"]
    # {"org_id": "ORG-ASEP1-AP-APNIC", "org_name": "Alibaba Cloud (Singapore) Private Limited", "country": "SG", "asns": [134963]}
    org_ids: List[str] = [
        "ORG-ASEP1-AP-APNIC",
    ]
