from cloudcheck.providers.base import BaseProvider
from typing import List


class Dell(BaseProvider):
    v2fly_company: str = "dell"
    tags: List[str] = ["cloud"]
    short_description: str = "Dell"
    long_description: str = "A multinational technology company that develops, sells, repairs, and supports computers and related products and services."
    # {"org_id": "DCC-25-ARIN", "org_name": "Dell, Inc.", "country": "US", "asns": [3612,3613,3614,3615,7977,12257,14876,17187,23144,30614,46507,46977,53878,54701,64208]}
    org_ids: List[str] = [
        "DCC-25-ARIN",
    ]
