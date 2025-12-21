from cloudcheck.providers.base import BaseProvider
from typing import List


class Leaseweb(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "Leaseweb"
    long_description: str = "A global hosting and cloud infrastructure provider offering dedicated servers, cloud hosting, and CDN services."
    # {"org_id": "LC-1193-ARIN", "org_name": "Leaseweb Canada Inc.", "country": "CA", "asns": [32613,32804,40699]}
    # {"org_id": "LU-76-ARIN", "org_name": "Leaseweb USA, Inc.", "country": "US", "asns": [7203]}
    # {"org_id": "LU-ARIN", "org_name": "Leaseweb USA, Inc.", "country": "US", "asns": [15003,19148,25847,27411,30633,393886,394380,395954,396190,396362]}
    # {"org_id": "ORG-FB8-RIPE", "org_name": "LeaseWeb Network B.V.", "country": "NL", "asns": [16265,38930,60626,202134,203774,203928]}
    # {"org_id": "ORG-LAPL4-AP-APNIC", "org_name": "LEASEWEB AUSTRALIA PTY LIMITED", "country": "AU", "asns": [136988]}
    # {"org_id": "ORG-LAPP1-AP-APNIC", "org_name": "LEASEWEB SINGAPORE PTE. LTD.", "country": "SG", "asns": [59253]}
    # {"org_id": "ORG-LHKL5-AP-APNIC", "org_name": "LEASEWEB HONG KONG LIMITED", "country": "HK", "asns": [133752]}
    # {"org_id": "ORG-LJK1-AP-APNIC", "org_name": "Leaseweb Japan K.K.", "country": "JP", "asns": [134351]}
    # {"org_id": "ORG-LUL9-RIPE", "org_name": "Leaseweb UK Limited", "country": "GB", "asns": [205544]}
    # {"org_id": "ORG-NA8-RIPE", "org_name": "Leaseweb Deutschland GmbH", "country": "DE", "asns": [28753]}
    # {"org_id": "ORG-OB3-RIPE", "org_name": "LeaseWeb Netherlands B.V.", "country": "NL", "asns": [60781]}
    org_ids: List[str] = [
        "LC-1193-ARIN",
        "LU-76-ARIN",
        "LU-ARIN",
        "ORG-FB8-RIPE",
        "ORG-LAPL4-AP-APNIC",
        "ORG-LAPP1-AP-APNIC",
        "ORG-LHKL5-AP-APNIC",
        "ORG-LJK1-AP-APNIC",
        "ORG-LUL9-RIPE",
        "ORG-NA8-RIPE",
        "ORG-OB3-RIPE",
    ]
