from .base import BaseCloudProvider


class Google(BaseCloudProvider):
    ips_url = "https://www.gstatic.com/ipranges/cloud.json"

    domains = [
        "googleapis.cn",
        "googleapis.com",
        "cloud.google.com",
        "gcp.gvt2.com",
        "appspot.com",
        "firebaseio.com",
        "google",
    ]

    bucket_name_regex = r"[a-z0-9][a-z0-9-_\.]{1,61}[a-z0-9]"
    firebase_bucket_name_regex = r"[a-z0-9][a-z0-9-\.]{1,61}[a-z0-9]"
    regexes = {
        "STORAGE_BUCKET": [
            r"(" + firebase_bucket_name_regex + r")\.(firebaseio\.com)",
            r"(" + bucket_name_regex + r")\.(storage\.googleapis\.com)",
        ]
    }

    def parse_response(self, response):
        ranges = set()
        for p in response.json()["prefixes"]:
            try:
                ranges.add(p["ipv4Prefix"])
            except KeyError:
                ranges.add(p["ipv6Prefix"])
        return ranges
