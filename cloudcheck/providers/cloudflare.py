from .base import BaseCloudProvider


class Cloudflare(BaseCloudProvider):
    ips_url = "https://api.cloudflare.com/client/v4/ips"
    provider_type = "cdn"

    def parse_response(self, response):
        ranges = set()
        response_json = response.json()
        for ip_type in ("ipv4_cidrs", "ipv6_cidrs"):
            for ip_range in response_json.get("result", {}).get(ip_type, []):
                ranges.add(ip_range)
        return ranges
