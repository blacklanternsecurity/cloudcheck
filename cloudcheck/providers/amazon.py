from .base import BaseCloudProvider


class Amazon(BaseCloudProvider):
    domains = [
        "amazon-dss.com",
        "amazonaws.com",
        "amazonaws.com.cn",
        "amazonaws.org",
        "amazonses.com",
        "amazonwebservices.com",
        "aws",
        "aws.a2z.com",
        "aws.amazon.com",
        "aws.dev",
        "awsstatic.com",
        "elasticbeanstalk.com",
    ]
    bucket_name_regex = r"[a-z0-9_][a-z0-9-\.]{1,61}[a-z0-9]"
    regexes = {
        "STORAGE_BUCKET": [
            r"(" + bucket_name_regex + r")\.(s3-?(?:[a-z0-9-]*\.){1,2}amazonaws\.com)"
        ]
    }

    ips_url = "https://ip-ranges.amazonaws.com/ip-ranges.json"

    def parse_response(self, response):
        return set(p["ip_prefix"] for p in response.json()["prefixes"])
