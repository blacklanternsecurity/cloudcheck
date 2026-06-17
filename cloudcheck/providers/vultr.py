from cloudcheck.providers.base import BaseProvider
from typing import List


class Vultr(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "Vultr"
    long_description: str = "A global cloud hosting provider offering SSD-based cloud compute, bare metal, and managed Kubernetes."
    # {"org_id": "CHOOP-1-ARIN", "org_name": "The Constant Company, LLC", "country": "US", "asns": [11508,20473,40504,46407,54094]}
    asns: List[int] = [11508, 20473, 40504, 46407, 54094]
    org_ids: List[str] = [
        "CHOOP-1-ARIN",
    ]
