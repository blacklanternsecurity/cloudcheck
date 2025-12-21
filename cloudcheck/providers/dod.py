from cloudcheck.providers.base import BaseProvider
from typing import List


class DoD(BaseProvider):
    """Department of Defense"""

    tags: List[str] = ["gov"]
    short_description: str = "Department of Defense"
    long_description: str = "A U.S. government agency responsible for coordinating and supervising all agencies and functions of the government directly related to national security and the United States Armed Forces."
    org_ids: List[str] = [
        "USDDD-ARIN",
    ]
    domains: List[str] = ["defense.gov", "war.gov", "mil"]

    # https://en.wikipedia.org/wiki/List_of_assigned_/8_IPv4_address_blocks
    cidrs: List[str] = [
        "6.0.0.0/8",  # Army Information Systems Center
        "7.0.0.0/8",  # DoD Network Information Center
        "11.0.0.0/8",  # DoD Intel Information Systems
        "21.0.0.0/8",  # DDN-RVN
        "22.0.0.0/8",  # Defense Information Systems Agency
        "26.0.0.0/8",  # Defense Information Systems Agency
        "28.0.0.0/8",  # DSI-North
        "29.0.0.0/8",  # Defense Information Systems Agency
        "30.0.0.0/8",  # Defense Information Systems Agency
        "33.0.0.0/8",  # DLA Systems Automation Center
        "55.0.0.0/8",  # DoD Network Information Center
        "214.0.0.0/8",  # DoD Network Information Center
        "215.0.0.0/8",  # DoD Network Information Center
    ]
