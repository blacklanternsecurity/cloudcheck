import io
import zipfile

from .base import BaseCloudProvider


class Akamai(BaseCloudProvider):
    domains = [
        "ak1.net",
        "aka-ai.com",
        "aka-ai.net",
        "akacrypto.net",
        "akadeem.net",
        "akadns.com",
        "akadns.net",
        "akadns6.net",
        "akaeai.com",
        "akafms.net",
        "akagtm.org",
        "akahost.net",
        "akaint.net",
        "akam.net",
        "akamaa.com",
        "akamah.com",
        "akamai-access.com",
        "akamai-access.net",
        "akamai-cdn.com",
        "akamai-platform-internal.net",
        "akamai-platform-staging.com",
        "akamai-platform.net",
        "akamai-regression.net",
        "akamai-staging.net",
        "akamai-sucks.net",
        "akamai-thailand.com",
        "akamai-thailand.net",
        "akamai-trials.com",
        "akamai.co.kr",
        "akamai.com",
        "akamai.net",
        "akamaiedge-staging.net",
        "akamaiedge.net",
        "akamaientrypoint.net",
        "akamaietpcnctest.com",
        "akamaietpcompromisedcnctest.com",
        "akamaietpcompromisedmalwaretest.com",
        "akamaietpmalwaretest.com",
        "akamaietpphishingtest.com",
        "akamaihd-staging.net",
        "akamaihd.com",
        "akamaihd.net",
        "akamaimagicmath.net",
        "akamainewzealand.com",
        "akamaiorigin-staging.net",
        "akamaiorigin.net",
        "akamaiphillipines.com",
        "akamaiphillipines.net",
        "akamaisingapore.net",
        "akamaistream.net",
        "akamaitech.com",
        "akamaitech.net",
        "akamaitechnologies.com",
        "akamaitechnologies.net",
        "akamaized-staging.net",
        "akamaized.net",
        "akamaizercentral.com",
        "akamak.com",
        "akamam.com",
        "akamci.com",
        "akami.com",
        "akami.net",
        "akamii.com",
        "akamqi.com",
        "akastream.com",
        "akastream.net",
        "akatns.net",
        "edgekey-staging.net",
        "edgekey.net",
        "edgesuite-staging.net",
        "edgesuite.net",
        "iamakamai.com",
        "iamakamai.net",
        "soasta-dswb.com",
        "srtcdn.net",
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
