from cloudcheck.providers.base import BaseProvider
from typing import List


class Qrator(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "Qrator"
    long_description: str = (
        "A DDoS protection and content delivery network service provider."
    )
    # {"org_id": "ORG-QLCS1-RIPE", "org_name": "Qrator Labs CZ s.r.o.", "country": "CZ", "asns": [200449,209671]}
    # {"org_id": "ORG-QTF1-RIPE", "org_name": "Qrator Technologies FZ-LLC", "country": "AE", "asns": [211112]}
    org_ids: List[str] = [
        "ORG-QLCS1-RIPE",
        "ORG-QTF1-RIPE",
    ]
