from .base import BaseCloudProvider


class Fastly(BaseCloudProvider):
    domains = [
        "fastly.com",
        "fastly.net",
        "fastlylabs.com",
        "fastlylb.net",
        "fastly-terrarium.com",
        # Video.js CDN
        "zencdn.net",
    ]

    ips_url = "https://api.fastly.com/public-ip-list"

    def parse_response(self, response):
        j = response.json()
        if j and isinstance(j, dict):
            addresses = j.get("addresses", [])
            if addresses and isinstance(addresses, list):
                return list(set(addresses))
