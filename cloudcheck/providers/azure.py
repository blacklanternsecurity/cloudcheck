from .base import BaseProvider
from typing import List, Dict


class Azure(BaseProvider):
    v2fly_company: str = "azure"
    tags: List[str] = ["cloud"]
    org_ids: List[str] = []
    _bucket_name_regex = r"[a-z0-9][a-z0-9-_\.]{1,61}[a-z0-9]"
    regexes: Dict[str, List[str]] = {
        "STORAGE_BUCKET_NAME": [_bucket_name_regex],
        "STORAGE_BUCKET_HOSTNAME": [r"(" + _bucket_name_regex + r")\.(blob\.core\.windows\.net)"]
    }

    _ips_url = "https://download.microsoft.com/download/0/1/8/018E208D-54F8-44CD-AA26-CD7BC9524A8C/PublicIPs_20200824.xml"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        for line in response.text.splitlines():
            if "IpRange Subnet" in line:
                ip_range = line.split('"')[1]
                ranges.add(ip_range)
        return list(ranges)

