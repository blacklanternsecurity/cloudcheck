from cloudcheck.providers.base import BaseProvider
from typing import List


class Navercloud(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "Naver Cloud Platform (네이버 클라우드 플랫폼)"
    long_description: str = (
        "A Korean cloud computing platform provided by Naver Corporation."
    )
    # "org_id": "@aut-23576-APNIC", "org_name": null, "country": null, "asns": [23576,23982]}
    # {"asn":23576,"asn_name":"nhn-AS-KR","org_id":"@aut-23576-APNIC"}
    org_ids: List[str] = [
        "@aut-23576-APNIC",
    ]
