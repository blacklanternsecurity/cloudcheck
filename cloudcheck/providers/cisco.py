from cloudcheck.providers.base import BaseProvider
from typing import List


class Cisco(BaseProvider):
    v2fly_company: str = "cisco"
    tags: List[str] = ["cloud"]
    # {"org_id": "CISCO-25-ARIN", "org_name": "Cisco Systems Inc.", "country": "US", "asns": [25949]}
    # {"org_id": "CISCO-32-ARIN", "org_name": "Cisco Systems, Inc.", "country": "US", "asns": [63096]}
    # {"org_id": "CISCOR-ARIN", "org_name": "CIS Corporation", "country": "US", "asns": [3792]}
    # {"org_id": "CISL-7-ARIN", "org_name": "Cisco Systems Ironport Division", "country": "US", "asns": [16417,30214,30215,30238,40427]}
    # {"org_id": "CS-2787-ARIN", "org_name": "Cisco Systems Inc", "country": "US", "asns": [398699]}
    # {"org_id": "CS-2821-ARIN", "org_name": "Cisco IoT", "country": "US", "asns": [36180,393544]}
    # {"org_id": "CS-2825-ARIN", "org_name": "Cisco Systems, Inc.", "country": "US", "asns": [396922]}
    # {"org_id": "CS-2831-ARIN", "org_name": "CISCO SYSTEMS, INC.", "country": "US", "asns": [109,2051,3943,22183,23460,26092,36519,40590,54140,399780]}
    # {"org_id": "CS-691-ARIN", "org_name": "Cisco Systems Cloud Division", "country": "US", "asns": [1343,32644]}
    # {"org_id": "CS-985-ARIN", "org_name": "Cisco Systems, Inc.", "country": "US", "asns": [55219]}
    # {"org_id": "OPEND-2-ARIN", "org_name": "Cisco OpenDNS, LLC", "country": "US", "asns": [25605,30607,36692]}
    # {"org_id": "ORG-CIL21-RIPE", "org_name": "Cisco International Limited", "country": "GB", "asns": [201799]}
    # {"org_id": "ORG-CL586-RIPE", "org_name": "CISCOM Ltd", "country": "RU", "asns": [61035]}
    # {"org_id": "ORG-CSNA1-RIPE", "org_name": "Cisco Systems Norway AS", "country": "NO", "asns": [58298]}
    # {"org_id": "WEX-ARIN", "org_name": "Cisco Webex LLC", "country": "US", "asns": [6577,13445,16472,26152,53258,399937]}
    org_ids: List[str] = [
        "CISCO-25-ARIN",
        "CISCO-32-ARIN",
        "CISCOR-ARIN",
        "CISL-7-ARIN",
        "CS-2787-ARIN",
        "CS-2821-ARIN",
        "CS-2825-ARIN",
        "CS-2831-ARIN",
        "CS-691-ARIN",
        "CS-985-ARIN",
        "OPEND-2-ARIN",
        "ORG-CIL21-RIPE",
        "ORG-CL586-RIPE",
        "ORG-CSNA1-RIPE",
        "WEX-ARIN",
    ]
