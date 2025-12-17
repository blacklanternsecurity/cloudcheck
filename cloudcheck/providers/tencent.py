from cloudcheck.providers.base import BaseProvider
from typing import List


class Tencent(BaseProvider):
    v2fly_company: str = "tencent"
    tags: List[str] = ["cloud"]
    # {"org_id": "ORG-STCS1-AP-APNIC", "org_name": "Shenzhen Tencent Computer Systems Company Limited", "country": "CN", "asns": [132203,132591]}
    # {"org_id": "ORG-TCCC1-AP-APNIC", "org_name": "Tencent Cloud Computing (Beijing) Co., Ltd", "country": "CN", "asns": [133478]}
    # {"org_id": "ORG-TCL14-AP-APNIC", "org_name": "Tencent (Thailand) Company Limited", "country": "TH", "asns": [137876]}
    org_ids: List[str] = [
        "ORG-STCS1-AP-APNIC",
        "ORG-TCCC1-AP-APNIC",
        "ORG-TCL14-AP-APNIC",
    ]
