import csv
import requests
import traceback
from pathlib import Path
from requests_cache import CachedSession
from requests_cache.backends import SQLiteCache

from .cidr import CidrRanges

db_path = Path.home() / ".cache" / "cloudcheck" / "requests-cache.sqlite"
backend = SQLiteCache(db_path=db_path)


class CloudProvider:
    main_url = ""

    def __init__(self, quiet=False, cache_for=None):
        self.quiet = quiet
        if cache_for is None:
            # default = cache IP lists for 7 days
            cache_for = 60 * 60 * 24 * 7
        self.session = CachedSession(expire_after=cache_for, backend=backend)
        self.ranges = CidrRanges(self.get_ranges())

    def get_ranges(self):
        try:
            response = self.session.get(self.main_url, allow_redirects=True)
            try:
                return self.parse_response(response)
            except Exception:
                self.print(f"Error parsing response: {traceback.format_exc()}")
        except requests.RequestException:
            self.print(f"Error retrieving {self.main_url}")
        return []

    def parse_response(self, response):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def print(self, s):
        if not self.quiet:
            print(f"[{self.name}] {s}")

    def __contains__(self, ip):
        return ip in self.ranges


class Azure(CloudProvider):
    main_url = "https://download.microsoft.com/download/0/1/8/018E208D-54F8-44CD-AA26-CD7BC9524A8C/PublicIPs_20200824.xml"

    def parse_response(self, response):
        ranges = set()
        for line in response.text.splitlines():
            if "IpRange Subnet" in line:
                ip_range = line.split('"')[1]
                ranges.add(ip_range)
        return ranges


class Amazon(CloudProvider):
    main_url = "https://ip-ranges.amazonaws.com/ip-ranges.json"

    def parse_response(self, response):
        return set(p["ip_prefix"] for p in response.json()["prefixes"])


class Google(CloudProvider):
    main_url = "https://www.gstatic.com/ipranges/cloud.json"

    def parse_response(self, response):
        ranges = set()
        for p in response.json()["prefixes"]:
            try:
                ranges.add(p["ipv4Prefix"])
            except KeyError:
                ranges.add(p["ipv6Prefix"])
        return ranges


class Oracle(CloudProvider):
    main_url = "https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json"

    def parse_response(self, response):
        ranges = set()
        for region in response.json()["regions"]:
            for cidr in region["cidrs"]:
                ranges.add(cidr["cidr"])
        return ranges


class DigitalOcean(CloudProvider):
    main_url = "https://digitalocean.com/geo/google.csv"

    def parse_response(self, response):
        do_ips = csv.DictReader(
            response.content.decode("utf-8").splitlines(),
            fieldnames=["range", "country", "region", "city", "postcode"],
        )
        ranges = set(i["range"] for i in do_ips)
        return ranges
