from cloudcheck.providers.base import BaseProvider
from typing import List


class Alibaba(BaseProvider):
    v2fly_company: str = "alibaba"
    tags: List[str] = ["cloud"]
    short_description: str = "Alibaba Cloud"
    long_description: str = "A Chinese cloud computing company and subsidiary of Alibaba Group, providing cloud services and infrastructure."
    # {"org_id": "ORG-ASEP1-AP-APNIC", "org_name": "Alibaba Cloud (Singapore) Private Limited", "country": "SG", "asns": [134963]}
    org_ids: List[str] = [
        "ORG-ASEP1-AP-APNIC",
    ]
