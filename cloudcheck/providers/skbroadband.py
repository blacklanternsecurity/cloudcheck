from cloudcheck.providers.base import BaseProvider
from typing import List


class Skbroadband(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "SK Broadband (SK브로드밴드)"
    long_description: str = "A Korean telecommunications company offering CDN services."
    # {"org_id": "@aut-10049-APNIC", "org_name": null, "country": null, "asns": [9705,10049]}
    # {"asn":10049,"asn_name":"SKNET-AS","country":null,"org":null,"org_id":"@aut-10049-APNIC"}
    org_ids: List[str] = [
        "@aut-10049-APNIC",
    ]
