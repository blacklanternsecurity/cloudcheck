from cloudcheck.providers.base import BaseProvider
from typing import List, Dict


class Amazon(BaseProvider):
    v2fly_company: str = "amazon"
    org_ids: List[str] = [
        "AMAZO-139-ARIN",  # Amazon.com, Inc., US
        "AMAZO-141-ARIN",  # Amazon Technologies, Inc., US
        "AMAZO-22-ARIN",  # Amazon Web Services, Inc., US
        "AMAZO-4-ARIN",  # Amazon.com, Inc., US
        "AMAZON-4-ARIN",  # Amazon.com, Inc., US
        "ARL-76-ARIN",  # Amazon Robotics LLC, US
        "ASL-830-ARIN",  # Amazon.com Services, LLC, US
        "AT-9049-ARIN",  # Amazon Technologies Inc., US
        "AT-9066-ARIN",  # Amazon Technologies Inc., US
        "ORG-AARP1-AP-APNIC",  # Amazon Asia-Pacific Resources Private Limited, SG
        "ORG-ACSP2-AP-APNIC",  # Amazon Corporate Services Pty Ltd, AU
        "ORG-ACTS1-AP-APNIC",  # Amazon Connection Technology Services (Beijing) Co., LTD, CN
        "ORG-ADSI1-RIPE",  # Amazon Data Services Ireland Ltd, IE
        "ORG-ADSJ1-AP-APNIC",  # Amazon Data Services Japan KK, JP
        "ORG-AI2-AP-APNIC",  # Amazon.com, Inc., US
    ]
    tags: List[str] = ["cloud"]
    _bucket_name_regex = r"[a-z0-9_][a-z0-9-\.]{1,61}[a-z0-9]"
    regexes: Dict[str, List[str]] = {
        "STORAGE_BUCKET_NAME": [_bucket_name_regex],
        "STORAGE_BUCKET_HOSTNAME": [
            r"(" + _bucket_name_regex + r")\.(s3-?(?:[a-z0-9-]*\.){1,2}amazonaws\.com)"
        ],
    }

    _ips_url = "https://ip-ranges.amazonaws.com/ip-ranges.json"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        return list(set(p["ip_prefix"] for p in response.json()["prefixes"]))
