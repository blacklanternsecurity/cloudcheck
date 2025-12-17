import csv
from cloudcheck.providers.base import BaseProvider
from typing import List, Dict


class DigitalOcean(BaseProvider):
    v2fly_company: str = "digitalocean"
    tags: List[str] = ["cloud"]
    # {"org_id": "DO-13-ARIN", "org_name": "DigitalOcean, LLC", "country": "US", "asns": [14061,46652,62567,393406,394362]}
    org_ids: List[str] = [
        "DO-13-ARIN",
    ]
    _bucket_name_regex = r"[a-z0-9][a-z0-9-]{2,62}"
    regexes: Dict[str, List[str]] = {
        "STORAGE_BUCKET_NAME": [_bucket_name_regex],
        "STORAGE_BUCKET_HOSTNAME": [
            r"(" + _bucket_name_regex + r")\.([a-z]{3}[\d]{1}\.digitaloceanspaces\.com)"
        ],
    }

    _ips_url = "https://www.digitalocean.com/geo/google.csv"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        do_ips = csv.DictReader(
            response.content.decode("utf-8").splitlines(),
            fieldnames=["range", "country", "region", "city", "postcode"],
        )
        ranges = set(i["range"] for i in do_ips)
        return list(ranges)
