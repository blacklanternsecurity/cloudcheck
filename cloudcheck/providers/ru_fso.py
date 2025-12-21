from cloudcheck.providers.base import BaseProvider
from typing import List


class RUFSO(BaseProvider):
    """Russian Federal Security Service"""

    tags: List[str] = ["gov"]
    short_description: str = "Russian Federal Security Service"
    long_description: str = "A Russian federal executive body responsible for counterintelligence, internal and border security, counterterrorism, and surveillance."
    org_ids: List[str] = [
        "ORG-TFGS1-RIPE",
    ]
