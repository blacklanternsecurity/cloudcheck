from .base import BaseCloudProvider


class Hetzner(BaseCloudProvider):
    domains = [
        "hetzner.de",
        "hetzner.com",
        "hetzner.cloude",
        "your-server.de",
        "your-objectstorage.com",
    ]

    bucket_name_regex = r"[a-z0-9][a-z0-9-_\.]{1,61}[a-z0-9]"
    regexes = {
        "STORAGE_BUCKET": [
            r"(" + bucket_name_regex + r")\.(your-objectstorage\.com)",
        ]
    }

    asns = [
        24940,
        212317,
        213230,
        215859,
    ]
