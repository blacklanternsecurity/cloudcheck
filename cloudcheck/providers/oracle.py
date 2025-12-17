from cloudcheck.providers.base import BaseProvider
from typing import List


class Oracle(BaseProvider):
    v2fly_company: str = "oracle"
    tags: List[str] = ["cloud"]
    # {"org_id": "ORACLE-4-ARIN", "org_name": "Oracle Corporation", "country": "US", "asns": [90,1630,3457,4184,4191,4192,6142,7160,10884,11049,11479,11506,11625,11887,13832,14506,14544,14919,15135,15179,18837,18916,20037,20054,22435,29976,31898,31925,33517,36282,40921,46403,46558,54253,63295,393218,393314,393676,393773,395010,395738,399966,401341]}
    # {"org_id": "ORACLE-4-Z-ARIN", "org_name": "Oracle Corporation", "country": "US", "asns": [792,793,794,1215,1216,1217,1218,1219]}
    # {"org_id": "ORG-OAI2-RIPE", "org_name": "Oracle America Inc.", "country": "US", "asns": [34135]}
    # {"org_id": "ORG-OC1-AP-APNIC", "org_name": "Oracle Corporation", "country": "US", "asns": [23885,24185,38538,136025]}
    # {"org_id": "ORG-OCMS1-AP-APNIC", "org_name": "ORACLE CUSTOMER MANAGEMENT SOLUTIONS PTY. LTD.", "country": "AU", "asns": [138207]}
    # {"org_id": "ORG-OSA29-RIPE", "org_name": "Oracle Svenska AB", "country": "SE", "asns": [15519,39467,43894,43898,52019,57748,60285,200705,200981,203267,206209]}
    org_ids: List[str] = [
        "ORACLE-4-ARIN",
        "ORACLE-4-Z-ARIN",
        "ORG-OAI2-RIPE",
        "ORG-OC1-AP-APNIC",
        "ORG-OCMS1-AP-APNIC",
        "ORG-OSA29-RIPE",
    ]

    _ips_url = "https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        for region in response.json()["regions"]:
            for cidr in region["cidrs"]:
                ranges.add(cidr["cidr"])
        return list(ranges)
