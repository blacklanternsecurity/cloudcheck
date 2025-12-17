from cloudcheck.providers.base import BaseProvider
from typing import List


class Rackspace(BaseProvider):
    tags: List[str] = ["cloud"]
    # {"org_id": "ORG-BEN1-RIPE", "org_name": "D-hosting die Rackspace & Connectivity GmbH", "country": "DE", "asns": [44716]}
    # {"org_id": "ORG-RA33-RIPE", "org_name": "Rackspace Ltd.", "country": "GB", "asns": [15395,39921,44009]}
    # {"org_id": "ORG-RGG2-RIPE", "org_name": "Rackspace Germany GmbH", "country": "DE", "asns": [213735,213740]}
    # {"org_id": "ORG-RHKL1-AP-APNIC", "org_name": "Rackspace.com Hong Kong Limited", "country": "HK", "asns": [45187,58683]}
    # {"org_id": "RACKS-8-ARIN", "org_name": "Rackspace Hosting", "country": "US", "asns": [10532,12200,19994,22720,27357,33070,33439,36248,54636,397485]}
    org_ids: List[str] = [
        "ORG-BEN1-RIPE",
        "ORG-RA33-RIPE",
        "ORG-RGG2-RIPE",
        "ORG-RHKL1-AP-APNIC",
        "RACKS-8-ARIN",
    ]
    domains: List[str] = [
        "rackspace.com",
    ]
