from cloudcheck.providers.base import BaseProvider
from typing import List


class Kinx(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "KINX (한국인터넷인프라)"
    long_description: str = (
        "A Korean content delivery network and cloud infrastructure provider."
    )
    # {"org_id": "@aut-9286-APNIC", "org_name": null, "country": null, "asns": [9286,9957,17604]}
    org_ids: List[str] = [
        "@aut-9286-APNIC",
    ]
