from cloudcheck.providers.base import BaseProvider
from typing import List


class Salesforce(BaseProvider):
    v2fly_company: str = "salesforce"
    tags: List[str] = ["cloud"]
    # {"org_id": "ORG-SI12-AP-APNIC", "org_name": "SalesForce.com, Inc.", "country": "US", "asns": [45422,133869,133942]}
    # {"org_id": "SALES-44-ARIN", "org_name": "Salesforce, Inc.", "country": "US", "asns": [393517,396417]}
    # {"org_id": "SALESF-3-ARIN", "org_name": "Salesforce.com, Inc.", "country": "US", "asns": [14340,22606,32542,32870,394808]}
    org_ids: List[str] = [
        "ORG-SI12-AP-APNIC",
        "SALES-44-ARIN",
        "SALESF-3-ARIN",
    ]
