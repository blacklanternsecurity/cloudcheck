import ipaddress
from cloudcheck.providers.base import BaseProvider
from typing import List


class Quiccloud(BaseProvider):
    v2fly_company: str = ""
    tags: List[str] = ["cdn"]
    short_description: str = "Quic.cloud"
    long_description: str = (
        "A content delivery network and edge computing platform providing CDN services."
    )
    # {"org_id": "QC-329-ARIN", "org_name": "QUIC CLOUD INC.", "country": "US", "asns": [26116]}
    org_ids: List[str] = [
        "QC-329-ARIN",
    ]

    _ips_url = "https://quic.cloud/ips"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        if getattr(response, "status_code", 0) == 200:
            text = response.text
            # Strip HTML tags
            text = (
                text.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
            )
            # Split by whitespace
            for token in text.split():
                token = token.strip()
                if token:
                    try:
                        ipaddress.ip_network(token, strict=False)
                        ranges.add(token)
                    except ValueError:
                        pass
        return list(ranges)
