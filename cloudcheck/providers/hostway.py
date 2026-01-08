from cloudcheck.providers.base import BaseProvider
from typing import List


class Hostway(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "Hostway (호스트웨이)"
    long_description: str = "A Korean cloud hosting and infrastructure provider."
    # {"org_id": "@aut-9952-APNIC", "org_name": null, "country": null, "asns": [9952]}
    # {"asn":9952,"asn_name":"HOSTWAY-AS-KR","org_id":"@aut-9952-APNIC"}
    org_ids: List[str] = [
        "@aut-9952-APNIC",
    ]
