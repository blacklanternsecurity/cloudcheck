from cloudcheck.providers.base import BaseProvider
from typing import List


class Bunnycdn(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "Bunny CDN"
    long_description: str = "A global content delivery network and edge platform."
    # {"org_id": "ORG-BISD2-RIPE", "org_name": "BUNNYWAY, informacijske storitve d.o.o.", "country": "SI", "asns": [200325]}
    asns: List[int] = [200325]
    org_ids: List[str] = [
        "ORG-BISD2-RIPE",
    ]
