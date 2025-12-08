import io
import zipfile
from .base import BaseProvider
from typing import List, Dict


class Akamai(BaseProvider):
    v2fly_company: str = "akamai"
    # asns from searching "akamai" on https://hackertarget.com/as-ip-lookup/
    # asns = [
    #     12222, 16625, 16702, 17204, 18680, 18717, 20189, 20940, 21342, 21357,
    #     21399, 22207, 22452, 23454, 23455, 23903, 24319, 26008, 30675, 31107,
    #     31108, 31109, 31110, 31377, 33047, 33905, 34164, 34850, 35204, 35993,
    #     35994, 36183, 39836, 43639, 45700, 55409, 55770, 63949, 133103, 393560,
    # ]
    tags: List[str] = ["cdn"]
    org_ids: List[str] = []

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

