from cloudcheck.providers.base import BaseProvider
from typing import List


class Nhncloud(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "NHN Cloud (NHN클라우드)"
    long_description: str = (
        "A Korean cloud computing platform provided by NHN Corporation."
    )
    # {"org_id": "@aut-10038-APNIC", "org_name": null, "country": null, "asns": [10038,45974,152291]}
    # {"asn":45974,"asn_name":"NHN-AS-KR","org_id":"@aut-10038-APNIC"}
    org_ids: List[str] = [
        "@aut-10038-APNIC",
    ]
