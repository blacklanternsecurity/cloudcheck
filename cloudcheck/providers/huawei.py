from cloudcheck.providers.base import BaseProvider
from typing import List


class Huawei(BaseProvider):
    v2fly_company: str = "huawei"
    tags: List[str] = ["cloud"]
    # {"org_id": "ORG-HIPL2-AP-APNIC", "org_name": "HUAWEI INTERNATIONAL PTE. LTD.", "country": "SG", "asns": [131444,136907,141180,149167,151610]}
    # {"org_id": "ORG-HT57-RIPE", "org_name": "HUAWEI TECHNOLOGIES(UK)CO.,LTD", "country": "GB", "asns": [206798]}
    # {"org_id": "ORG-HT61-RIPE", "org_name": "Huawei Tech(UAE)FZ-LLC", "country": "AE", "asns": [206204]}
    # {"org_id": "ORG-HTB10-RIPE", "org_name": "Huawei Technologies (Netherlands) B.V.", "country": "NL", "asns": [200756]
    org_ids: List[str] = [
        "ORG-HIPL2-AP-APNIC",
        "ORG-HT57-RIPE",
        "ORG-HT61-RIPE",
        "ORG-HTB10-RIPE",
    ]
