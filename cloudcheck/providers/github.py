import ipaddress
import os
from cloudcheck.providers.base import BaseProvider
from typing import List


class GitHub(BaseProvider):
    v2fly_company: str = "github"
    tags: List[str] = ["cdn"]
    short_description: str = "GitHub"
    long_description: str = "A web-based platform for version control and collaboration using Git, providing hosting for software development and code repositories."
    # {"org_id": "GITHU-ARIN", "org_name": "GitHub, Inc.", "country": "US", "asns": [36459]}
    org_ids: List[str] = [
        "GITHU-ARIN",
    ]

    _ips_url = "https://api.github.com/meta"

    def fetch_cidrs(self):
        # Unauthenticated, the API allows 60 requests an hour per IP, which shared CI runners use up.
        # A rate-limited reply has no IP lists, so the provider silently dropped to its ASN ranges.
        headers = {}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        # No redirects, so the token only ever goes to api.github.com.
        response = self.request(self._ips_url, headers=headers, follow_redirects=False)
        if not response.is_success:
            raise RuntimeError(
                f"{self._ips_url} returned HTTP {response.status}: {response.text[:300]}"
            )
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
        if not ranges:
            raise RuntimeError(
                f"{self._ips_url} returned no IP ranges: {response.text[:300]}"
            )
        return list(ranges)
