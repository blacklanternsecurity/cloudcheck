import ipaddress
import os
import sys
from cloudcheck.providers.base import BaseProvider
from typing import List

_warned_missing_github_token = False


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

    def _get_meta(self, token):
        # The token goes on this request only. helpers.request() serves every provider's
        # third-party host, so it must never carry a GitHub credential.
        headers = {
            "accept": "application/vnd.github+json",
            "x-github-api-version": "2022-11-28",
        }
        if token:
            headers["authorization"] = f"Bearer {token}"
        return self.request(self._ips_url, headers=headers)

    def fetch_cidrs(self):
        global _warned_missing_github_token
        # Unauthenticated, /meta shares a 60 requests/hour budget with every other job on
        # the runner's IP, and a rate-limited response used to parse as "no ranges".
        token = os.getenv("GITHUB_TOKEN")
        if not token and not _warned_missing_github_token:
            _warned_missing_github_token = True
            print(
                "WARNING: GITHUB_TOKEN env var is not set; api.github.com/meta will be "
                "requested unauthenticated and may be rate-limited.",
                file=sys.stderr,
            )
        response = self._get_meta(token)
        if token and response.status_code == 401:
            # A stale or revoked token must not do worse than no token.
            print(
                "WARNING: GITHUB_TOKEN was rejected by api.github.com (401); retrying unauthenticated.",
                file=sys.stderr,
            )
            response = self._get_meta(None)
        if response.status_code != 200:
            headers = response.headers
            raise RuntimeError(
                f"{self._ips_url} returned HTTP {response.status_code} "
                f"(x-ratelimit-remaining={headers.get('x-ratelimit-remaining')}, "
                f"x-ratelimit-reset={headers.get('x-ratelimit-reset')})"
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
            raise RuntimeError(f"{self._ips_url} returned HTTP 200 but no IP ranges")
        return list(ranges)
