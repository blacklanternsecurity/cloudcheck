from .base import BaseCloudProvider


class Amazon(BaseCloudProvider):
    # https://github.com/v2fly/domain-list-community/blob/master/data/aws
    domains = [
        "acmvalidations.com",
        "acmvalidationsaws.com",
        "aesworkshops.com",
        "amazon-dss.com",
        "amazonaws-china.com",
        "amazonaws.co.uk",
        "amazonaws.com.cn",
        "amazonaws.com",
        "amazonaws.org",
        "amazonaws.tv",
        "amazonses.com",
        "amazonwebservices.com",
        "amazonworkdocs.com",
        "amplifyapp.com",
        "amplifyframework.com",
        "aws-iot-hackathon.com",
        "aws.a2z.com",
        "aws.amazon.com",
        "aws.dev",
        "aws",
        "awsautopilot.com",
        "awsautoscaling.com",
        "awsbraket.com",
        "awscommandlineinterface.com",
        "awsedstart.com",
        "awseducate.com",
        "awseducate.net",
        "awseducate.org",
        "awsglobalaccelerator.com",
        "awsloft-johannesburg.com",
        "awsloft-stockholm.com",
        "awssecworkshops.com",
        "awsstatic.com",
        "awsthinkbox.com",
        "awstrack.me",
        "cdkworkshop.com",
        "cloudfront.com",
        "cloudfront.net",
        "containersonaws.com",
        "elasticbeanstalk.com",
        "thinkboxsoftware.com",
    ]
    bucket_name_regex = r"[a-z0-9_][a-z0-9-\.]{1,61}[a-z0-9]"
    regexes = {"STORAGE_BUCKET": [r"(" + bucket_name_regex + r")\.(s3-?(?:[a-z0-9-]*\.){1,2}amazonaws\.com)"]}

    ips_url = "https://ip-ranges.amazonaws.com/ip-ranges.json"

    def parse_response(self, response):
        return set(p["ip_prefix"] for p in response.json()["prefixes"])
