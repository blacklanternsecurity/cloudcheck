from cloudcheck.providers.base import BaseProvider
from typing import List


class FBI(BaseProvider):
    """Federal Bureau of Investigation"""

    tags: List[str] = ["gov"]
    short_description: str = "Federal Bureau of Investigation"
    long_description: str = "A U.S. government agency that serves as the domestic intelligence and security service, responsible for investigating federal crimes and protecting national security."
    org_ids: List[str] = [
        "FCJIS-ARIN",  # Federal Criminal Justice Information Services
    ]
    domains: List[str] = [
        "fbi.gov",
        "fbijobs.gov",
        "ic3.gov",
    ]
