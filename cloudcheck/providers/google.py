from cloudcheck.providers.base import BaseProvider
from typing import List, Dict


class Google(BaseProvider):
    v2fly_company: str = "google"
    # domains = ["googleapis.cn", "googleapis.com", "cloud.google.com", "gcp.gvt2.com", "appspot.com", "firebaseio.com", "google"]
    tags: List[str] = ["cloud"]
    # {"org_id": "GAL-53-ARIN", "org_name": "Google Access LLC", "country": "US", "asns": [32381]}
    # {"org_id": "GF-ARIN", "org_name": "Google Fiber Inc.", "country": "US", "asns": [6432,16591,19448]}
    # {"org_id": "GL-946-ARIN", "org_name": "Google LLC", "country": "US", "asns": [33715]}
    # {"org_id": "GOGL-ARIN", "org_name": "Google LLC", "country": "US", "asns": [13949,15169,19425,22577,22859,26684,36039,36040,40873]}
    # {"org_id": "GOOGL-1-ARIN", "org_name": "Google LLC", "country": "US", "asns": [36383,36384,36385,36411,36520]}
    # {"org_id": "GOOGL-2-ARIN", "org_name": "Google LLC", "country": "US", "asns": [16550,19527,26910,36561,55023,394089,395973,396178,396982]}
    # {"org_id": "GOOGL-5-ARIN", "org_name": "Google LLC", "country": "US", "asns": [394639]}
    # {"org_id": "GOOGL-9-ARIN", "org_name": "Google LLC", "country": "US", "asns": [394507]}
    # {"org_id": "GOOGL-ARIN", "org_name": "Google, LLC", "country": "US", "asns": [36492]}
    # {"org_id": "ORG-GAPP2-AP-APNIC", "org_name": "Google Asia Pacific Pte. Ltd.", "country": "SG", "asns": [139070,139190]}
    # {"org_id": "ORG-GCEL1-RIPE", "org_name": "Google Cloud EMEA Ltd", "country": "IE", "asns": [209504,209519,209539,214609,214611]}
    # {"org_id": "ORG-GIL4-RIPE", "org_name": "Google Ireland Limited", "country": "IE", "asns": [43515]}
    # {"org_id": "ORG-GKL1-AFRINIC", "org_name": "Google Kenya Limited", "country": "KE", "asns": [36987]}
    # {"org_id": "ORG-GSG10-RIPE", "org_name": "Google Switzerland GmbH", "country": "CH", "asns": [41264]}
    # {"org_id": "ORG-GSPL5-AP-APNIC", "org_name": "Google Singapore Pte. Ltd.", "country": "SG", "asns": [45566]}
    org_ids: List[str] = [
        "GAL-53-ARIN",
        "GF-ARIN",
        "GL-946-ARIN",
        "GOGL-ARIN",
        "GOOGL-1-ARIN",
        "GOOGL-2-ARIN",
        "GOOGL-5-ARIN",
        "GOOGL-9-ARIN",
        "GOOGL-ARIN",
        "ORG-GAPP2-AP-APNIC",
        "ORG-GCEL1-RIPE",
        "ORG-GIL4-RIPE",
        "ORG-GKL1-AFRINIC",
        "ORG-GSG10-RIPE",
        "ORG-GSPL5-AP-APNIC",
    ]
    _bucket_name_regex = r"[a-z0-9][a-z0-9-_\.]{1,61}[a-z0-9]"
    _firebase_bucket_name_regex = r"[a-z0-9][a-z0-9-\.]{1,61}[a-z0-9]"
    regexes: Dict[str, List[str]] = {
        "STORAGE_BUCKET_NAME": [_bucket_name_regex, _firebase_bucket_name_regex],
        "STORAGE_BUCKET_HOSTNAME": [
            r"(" + _firebase_bucket_name_regex + r")\.(firebaseio\.com)",
            r"(" + _bucket_name_regex + r")\.(storage\.googleapis\.com)",
        ],
    }

    _ips_url = "https://www.gstatic.com/ipranges/cloud.json"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        for p in response.json()["prefixes"]:
            try:
                ranges.add(p["ipv4Prefix"])
            except KeyError:
                ranges.add(p["ipv6Prefix"])
        return list(ranges)
