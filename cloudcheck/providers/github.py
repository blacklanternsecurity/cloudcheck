import ipaddress

from .base import BaseCloudProvider


class GitHub(BaseCloudProvider):
    ips_url = "https://api.github.com/meta"
    domains = ["github.com"]
    provider_type = "cdn"

    def parse_response(self, response):
        ranges = set()
        response_json = response.json()
        for k, v in response_json.items():
            if isinstance(v, list):
                for n in v:
                    try:
                        ipaddress.ip_network(n)
                        ranges.add(n)
                    except ValueError:
                        pass
        return ranges
