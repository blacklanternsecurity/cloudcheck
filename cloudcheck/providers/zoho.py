from cloudcheck.providers.base import BaseProvider
from typing import List


class Zoho(BaseProvider):
    v2fly_company: str = "zoho"
    # {"org_id": "ORG-ZCB1-RIPE", "org_name": "ZOHO Corporation B.V", "country": "NL", "asns": [205111]}
    # {"org_id": "ORG-ZCPL1-AP-APNIC", "org_name": "ZOHO Corporation Private Limited", "country": "IN", "asns": [56201]}
    # {"org_id": "ORG-ZCPL2-AP-APNIC", "org_name": "Zoho Corporation PTY LTD", "country": "AU", "asns": [139006]}
    # {"org_id": "ORG-ZCPL4-AP-APNIC", "org_name": "ZOHO CORPORATION PTE. LTD.", "country": "SG", "asns": [135102]}
    # {"org_id": "ORG-ZJC1-AP-APNIC", "org_name": "Zoho Japan Corporation", "country": "JP", "asns": [141757]}
    # {"org_id": "ORG-ZSTL1-RIPE", "org_name": "Zoho Software Trading LLC", "country": "AE", "asns": [214227]}
    # {"org_id": "ZCC-22-ARIN", "org_name": "Zoho Canada Corporation", "country": "CA", "asns": [401636]}
    # {"org_id": "ZOHOC-ARIN", "org_name": "ZOHO", "country": "US", "asns": [2639,397849,400780]}
    tags: List[str] = ["cloud"]
    org_ids: List[str] = [
        "ORG-ZCB1-RIPE",
        "ORG-ZCPL1-AP-APNIC",
        "ORG-ZCPL2-AP-APNIC",
        "ORG-ZCPL4-AP-APNIC",
        "ORG-ZJC1-AP-APNIC",
        "ORG-ZSTL1-RIPE",
        "ZCC-22-ARIN",
        "ZOHOC-ARIN",
    ]
