from .base import BaseCloudProvider


class Oracle(BaseCloudProvider):
    ips_url = "https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json"

    def parse_response(self, response):
        ranges = set()
        for region in response.json()["regions"]:
            for cidr in region["cidrs"]:
                ranges.add(cidr["cidr"])
        return ranges
