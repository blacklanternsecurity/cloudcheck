from cloudcheck.providers.base import BaseProvider
from typing import List


class IBM(BaseProvider):
    v2fly_company: str = "ibm"
    tags: List[str] = ["cloud"]
    # {"org_id": "AWDIC-ARIN", "org_name": "Advanced Workstations Division, IBM Corporation", "country": "US", "asns": [706]}
    # {"org_id": "IAD-7-ARIN", "org_name": "IBM AS/400 Division", "country": "US", "asns": [10337]}
    # {"org_id": "IBM-1-ARIN", "org_name": "IBM", "country": "US", "asns": [763,10676,12237,15293,17390,18703,19152,19604,19898,22722,23145,23257,26543,27477,27530,29834,393850,395473]}
    # {"org_id": "IBM-1-Z-ARIN", "org_name": "IBM", "country": "US", "asns": [163,547,1747,1786,1956,1997,2538,3082,3383]}
    # {"org_id": "IBM-43-ARIN", "org_name": "IBM", "country": "US", "asns": [2560]}
    # {"org_id": "IBMC-14-ARIN", "org_name": "IBM Corporation", "country": "US", "asns": [19765]}
    # {"org_id": "IBMC-24-ARIN", "org_name": "IBM Cloud", "country": "US", "asns": [13749,13884,21844,30315,36351,36420,46702,46703,46704]}
    # {"org_id": "IBML-1-ARIN", "org_name": "ibml", "country": "US", "asns": [40847]}
    # {"org_id": "ICNS-4-ARIN", "org_name": "IBM Canada Network Services Company", "country": "CA", "asns": [3059]}
    # {"org_id": "ORG-ACL6-AP-APNIC", "org_name": "FIBMESH IN LIMITED", "country": "IN", "asns": [133082,149779]}
    # {"org_id": "ORG-CIF2-RIPE", "org_name": "COMPAGNIE IBM FRANCE SAS", "country": "FR", "asns": [202213]}
    # {"org_id": "ORG-IBBC1-RIPE", "org_name": "IBM BTO Business Consulting Services Sp. z o.o.", "country": "PL", "asns": [200138]}
    # {"org_id": "ORG-IBMC1-RIPE", "org_name": "INTERNATIONAL BUSINESS MACHINES CORPORATION", "country": "US", "asns": [204764,209394]}
    # {"org_id": "ORG-IBMO1-RIPE", "org_name": "International Business Machines of Belgium Ltd", "country": "BE", "asns": [15776]}
    # {"org_id": "ORG-IBSI1-AP-APNIC", "org_name": "IBM Business Services, Inc", "country": "PH", "asns": [133377]}
    # {"org_id": "ORG-IDG12-RIPE", "org_name": "IBM Deutschland GmbH", "country": "DE", "asns": [214585]}
    # {"org_id": "ORG-IIAT1-RIPE", "org_name": "IBM Israel-Science and technology Ltd.", "country": "IL", "asns": [50995]}
    # {"org_id": "ORG-INZL1-AP-APNIC", "org_name": "IBM New Zealand Limited", "country": "NZ", "asns": [24189]}
    # {"org_id": "ORG-IR9-RIPE", "org_name": "IBM Romania SRL", "country": "RO", "asns": [61179]}
    # {"org_id": "ORG-IRS1-RIPE", "org_name": "IBM Romania S.R.L.", "country": "RO", "asns": [43283]}
    # {"org_id": "ORG-ISPL9-AP-APNIC", "org_name": "IBM Singapore Pte Ltd", "country": "SG", "asns": [10120,134667,135291,136468,138450]}
    # {"org_id": "ORG-IUL5-RIPE", "org_name": "IBM United Kingdom Limited", "country": "GB", "asns": [203652]}
    # {"org_id": "ORG-LS306-RIPE", "org_name": "LTD SibMediaFon", "country": "RU", "asns": [48507]}
    # {"org_id": "ORG-SCG6-RIPE", "org_name": "IBM Deutschland GmbH", "country": "DE", "asns": [50524]}
    org_ids: List[str] = [
        "AWDIC-ARIN",
        "IAD-7-ARIN",
        "IBM-1-ARIN",
        "IBM-1-Z-ARIN",
        "IBM-43-ARIN",
        "IBMC-14-ARIN",
        "IBMC-24-ARIN",
        "IBML-1-ARIN",
        "ICNS-4-ARIN",
        "ORG-ACL6-AP-APNIC",
        "ORG-CIF2-RIPE",
        "ORG-IBBC1-RIPE",
        "ORG-IBMC1-RIPE",
        "ORG-IBMO1-RIPE",
        "ORG-IBSI1-AP-APNIC",
        "ORG-IDG12-RIPE",
        "ORG-IIAT1-RIPE",
        "ORG-INZL1-AP-APNIC",
        "ORG-IR9-RIPE",
        "ORG-IRS1-RIPE",
        "ORG-ISPL9-AP-APNIC",
        "ORG-IUL5-RIPE",
        "ORG-LS306-RIPE",
        "ORG-SCG6-RIPE",
    ]
