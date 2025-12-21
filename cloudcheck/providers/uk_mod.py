from cloudcheck.providers.base import BaseProvider
from typing import List


class UKMoD(BaseProvider):
    """United Kingdom Ministry of Defense"""

    tags: List[str] = ["gov"]
    short_description: str = "United Kingdom Ministry of Defence"
    long_description: str = "A U.K. government department responsible for implementing the defence policy of the United Kingdom and managing the British Armed Forces."
    org_ids: List[str] = [
        "ORG-DMOD1-RIPE",
    ]
    domains: List[str] = [
        "gov.uk",
    ]
