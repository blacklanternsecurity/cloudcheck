import csv

from .base import BaseCloudProvider


class DigitalOcean(BaseCloudProvider):
    domains = [
        "digitalocean.com",
        "digitaloceanspaces.com",
        "do.co",
        "nginxconfig.io",
    ]

    bucket_name_regex = r"[a-z0-9][a-z0-9-]{2,62}"
    regexes = {"STORAGE_BUCKET": [r"(" + bucket_name_regex + r")\.([a-z]{3}[\d]{1}\.digitaloceanspaces\.com)"]}

    ips_url = "https://digitalocean.com/geo/google.csv"

    def parse_response(self, response):
        do_ips = csv.DictReader(
            response.content.decode("utf-8").splitlines(),
            fieldnames=["range", "country", "region", "city", "postcode"],
        )
        ranges = set(i["range"] for i in do_ips)
        return ranges
