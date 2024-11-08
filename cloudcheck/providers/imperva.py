from .base import BaseCloudProvider


class Imperva(BaseCloudProvider):
    provider_type = "cdn"
    domains = [
        "imperva.com",
    ]
    asns = [
        62571,
    ]
    ips_url = "https://my.imperva.com/api/integration/v1/ips"

    def parse_response(self, response):
        ranges = set()
        data = response.json()
        for ipv4 in data.get("ipRanges", []):
            ranges.add(ipv4)
        for ipv6 in data.get("ipv6Ranges", []):
            ranges.add(ipv6)
        return ranges
