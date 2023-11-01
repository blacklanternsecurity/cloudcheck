import io
import zipfile

from .base import BaseCloudProvider


class Akamai(BaseCloudProvider):
    domains = [
        "akadns.net",
        "akamai-staging.net",
        "akamai.net",
        "akamaiedge-staging.net",
        "akamaiedge.net",
        "akamaihd-staging.net",
        "akamaihd.net",
        "akamaiorigin-staging.net",
        "akamaiorigin.net",
        "akamaized-staging.net",
        "akamaized.net",
        "edgekey-staging.net",
        "edgekey.net",
        "edgesuite-staging.net",
        "edgesuite.net",
    ]
    ips_url = "https://techdocs.akamai.com/property-manager/pdfs/akamai_ipv4_ipv6_CIDRs-txt.zip"
    provider_type = "cdn"

    def parse_response(self, response):
        ranges = set()
        content = getattr(response, "content", b"")
        # Extract the contents of the zip file to memory
        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            for filename in ("akamai_ipv4_CIDRs.txt", "akamai_ipv6_CIDRs.txt"):
                with zip_file.open(filename) as f:
                    for line in f.read().splitlines():
                        line = line.decode(errors="ignore").strip()
                        if line:
                            ranges.add(line)
        return ranges
