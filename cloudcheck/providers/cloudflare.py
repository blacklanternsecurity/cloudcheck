from .base import BaseCloudProvider


class Cloudflare(BaseCloudProvider):
    ips_url = "https://api.cloudflare.com/client/v4/ips"
    # https://github.com/v2fly/domain-list-community/blob/master/data/cloudflare
    domains = [
        "argotunnel.com",
        "cloudflare-dns.com",
        "cloudflare-ech.com",
        "cloudflare-gateway.com",
        "cloudflare-quic.com",
        "cloudflare.com",
        "cloudflare.net",
        "cloudflare.tv",
        "cloudflareaccess.com",
        "cloudflareapps.com",
        "cloudflarebolt.com",
        "cloudflareclient.com",
        "cloudflareinsights.com",
        "cloudflareok.com",
        "cloudflareportal.com",
        "cloudflarepreview.com",
        "cloudflareresolve.com",
        "cloudflaressl.com",
        "cloudflarestatus.com",
        "cloudflarestorage.com",
        "cloudflarestream.com",
        "cloudflaretest.com",
        "cloudflarewarp.com",
        "every1dns.net",
        "one.one.one",
        "pacloudflare.com",
        "pages.dev",
        "trycloudflare.com",
        "videodelivery.net",
        "warp.plus",
        "workers.dev",
        "r2.dev",
    ]

    bucket_name_regex = r"[a-z0-9_][a-z0-9-\.]{1,61}[a-z0-9]"
    regexes = {
        "STORAGE_BUCKET": [
            r"(" + bucket_name_regex + r")\.(r2\.dev)",
            r"(" + bucket_name_regex + r")\.(r2\.cloudflarestorage\.com)",
        ]
    }

    provider_type = "cdn"

    def parse_response(self, response):
        ranges = set()
        response_json = response.json()
        for ip_type in ("ipv4_cidrs", "ipv6_cidrs"):
            for ip_range in response_json.get("result", {}).get(ip_type, []):
                ranges.add(ip_range)
        return ranges
