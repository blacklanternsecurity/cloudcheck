import io
import zipfile
from cloudcheck.providers.base import BaseProvider
from typing import List


class Akamai(BaseProvider):
    v2fly_company: str = "akamai"
    tags: List[str] = ["cloud"]
    # {"org_id": "AKAMAI-ARIN", "org_name": "Akamai Technologies, Inc.", "country": "US", "asns": [12222,16625,16702,17204,17334,18680,18717,20189,22207,22452,23454,23455,26008,30675,31984,32787,33047,35993,35994,36029,36183,393234,393560]}
    # {"org_id": "ORG-AT1-RIPE", "org_name": "Akamai International B.V.", "country": "NL", "asns": [20940,21342,21357,21399,31107,31108,31109,31110,31377,33905,34164,34850,35204,39836,43639,48163,49249,49846,200005,213120]}
    # {"org_id": "ORG-ATI1-AP-APNIC", "org_name": "Akamai Technologies, Inc.", "country": "US", "asns": [23903,24319,45757,55409,55770,63949,133103]}
    org_ids: List[str] = [
        "AKAMAI-ARIN",
        "ORG-AT1-RIPE",
        "ORG-ATI1-AP-APNIC",
    ]

    _ips_url = "https://techdocs.akamai.com/property-manager/pdfs/akamai_ipv4_ipv6_CIDRs-txt.zip"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        content = getattr(response, "content", b"")
        # Extract the contents of the zip file to memory
        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            for filename in ("akamai_ipv4_CIDRs.txt", "akamai_ipv6_CIDRs.txt"):
                with zip_file.open(filename) as f:
                    for line in f.read().splitlines():
                        line = line.decode(errors="ignore").strip()
                        if line:
                            ranges.add(line)
        return list(ranges)
