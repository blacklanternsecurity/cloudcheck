from cloudcheck.providers.base import BaseProvider
from typing import List


class Gabia(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "Gabia (가비아)"
    long_description: str = "A Korean cloud hosting and infrastructure provider."
    # {"org_id": "@aut-17589-APNIC", "org_name": null, "country": null, "asns": [17589]}
    org_ids: List[str] = [
        "@aut-17589-APNIC",
    ]
