from cloudcheck.providers.base import BaseProvider
from typing import List


class Sucuri(BaseProvider):
    tags: List[str] = ["waf"]
    short_description: str = "Sucuri"
    long_description: str = (
        "A website security and web application firewall service provider."
    )
    # {"org_id": "SUCUR-2-ARIN", "org_name": "Sucuri", "country": "US", "asns": [30148]}
    org_ids: List[str] = [
        "SUCUR-2-ARIN",
    ]
