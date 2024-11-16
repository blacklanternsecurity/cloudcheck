from .base import BaseCloudProvider


class Arvancloud(BaseCloudProvider):
    ips_url = "https://www.arvancloud.ir/en/ips.txt"
    domains = [
        "arvancloud.ir",
    ]
    asns = [
        57568,
        205585,
        208006,
        210296,
    ]

    provider_type = "cdn"

    def parse_response(self, response):
        ranges = set()
        if getattr(response, "status_code", 0) == 200:
            ranges.update(response.text.splitlines())
        return ranges
