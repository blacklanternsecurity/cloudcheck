from cloudcheck.providers.base import BaseProvider
from typing import List


class Zscaler(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "Zscaler"
    long_description: str = "A cloud security company providing secure internet access, cloud security, and zero trust network access services."

    _ips_url = "https://api.config.zscaler.com/zscaler.net/cenr/json"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        if getattr(response, "status_code", 0) == 200:
            response_json = response.json()
            if isinstance(response_json, dict):
                for domain, data in response_json.items():
                    for continent, cities in data.items():
                        for city, ranges_list in cities.items():
                            for range_data in ranges_list:
                                range_str = range_data.get("range")
                                if range_str:
                                    ranges.add(range_str)
        return list(ranges)
