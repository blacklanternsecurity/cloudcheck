from cloudcheck.providers.base import BaseProvider
from typing import List


class Scaleway(BaseProvider):
    tags: List[str] = ["cloud"]
    # {"org_id": "ORG-TT1-RIPE", "org_name": "SCALEWAY S.A.S.", "country": "FR", "asns": [12876,29447,202023]}
    # {"org_id": "SUC-48-ARIN", "org_name": "SCALEWAY US CORPORATION", "country": "US", "asns": [54265]}
    org_ids: List[str] = [
        "ORG-TT1-RIPE",
        "SUC-48-ARIN",
    ]
    domains: List[str] = [
        "scaleway.com",
    ]
