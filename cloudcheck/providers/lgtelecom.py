from cloudcheck.providers.base import BaseProvider
from typing import List


class Lgtelecom(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "LG U+ (LG유플러스)"
    long_description: str = "A Korean telecommunications company offering CDN services."
    # {"org_id": "@aut-17853-APNIC", "org_name": null, "country": null, "asns": [17853]}
    # {"asn":17853,"asn_name":"LGTELECOM-AS-KR","org_id":"@aut-17853-APNIC"}
    org_ids: List[str] = [
        "@aut-17853-APNIC",
    ]
