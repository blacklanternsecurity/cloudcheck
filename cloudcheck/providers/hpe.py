from cloudcheck.providers.base import BaseProvider
from typing import List


class HPE(BaseProvider):
    # Hewlett Packard Enterprise Development, L.P.
    v2fly_company: str = "hpe"
    tags: List[str] = ["cloud"]
    # {"org_id": "HPE-15-ARIN", "org_name": "HEWLETT PACKARD ENTERPRISE COMPANY", "country": "US", "asns": [157,1033,1034,13481,20096,22149,25867,27510,40617,395714,395992,396063,397363,397957,398199,399185,399610,400054,400624,400737,400763]}
    org_ids: List[str] = [
        "HPE-15-ARIN",
    ]
