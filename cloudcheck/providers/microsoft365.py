from cloudcheck.providers.base import BaseProvider
from typing import List


class Microsoft365(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "Microsoft 365"
    long_description: str = "A cloud-based productivity suite provided by Microsoft, including Office applications and cloud services."

    _ips_url = "https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        if getattr(response, "status_code", 0) == 200:
            response_json = response.json()
            if isinstance(response_json, list):
                for item in response_json:
                    if isinstance(item, dict):
                        ranges.update(item.get("ips", []))
        return list(ranges)

    def fetch_domains(self):
        response = self.request(self._ips_url)
        domains = set()
        if getattr(response, "status_code", 0) == 200:
            response_json = response.json()
            if isinstance(response_json, list):
                for item in response_json:
                    if isinstance(item, dict):
                        for domain in item.get("urls", []):
                            domains.add(domain.strip("*."))
        return list(domains)
