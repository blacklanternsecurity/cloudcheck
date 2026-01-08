from cloudcheck.providers.base import BaseProvider
from typing import List


class Baidu(BaseProvider):
    v2fly_company: str = "baidu"
    tags: List[str] = ["cdn"]
    short_description: str = "Baidu Cloud Acceleration (百度云加速)"
    long_description: str = "A Chinese content delivery network and cloud acceleration service provided by Baidu."
    # {"org_id": "BUL-5-ARIN", "org_name": "Baidu USA LLC", "country": "US", "asns": [63288]}
    # {"org_id": "ORG-BKL1-AP-APNIC", "org_name": "Baidu (Hong Kong) Limited", "country": "HK", "asns": [133746]}
    # {"org_id": "ORG-BKL4-RIPE", "org_name": "Baidu (Hong Kong) Limited", "country": "HK", "asns": [199506]}
    org_ids: List[str] = [
        "BUL-5-ARIN",
        "ORG-BKL1-AP-APNIC",
        "ORG-BKL4-RIPE",
    ]
