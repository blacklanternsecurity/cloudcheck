from .base import BaseCloudProvider


class Cloudfront(BaseCloudProvider):
    ips_url = "https://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips"
    # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/LocationsOfEdgeServers.html
    domains = [
        "cloudfront.com",
        "cloudfront.net",
    ]

    provider_type = "cdn"

    def parse_response(self, response):
        ranges = set()
        response_json = response.json()
        if not isinstance(response_json, dict):
            raise ValueError(f"Invalid response format: {type(response_json)}")
        for r in response_json.values():
            ranges.update(r)
        return ranges
