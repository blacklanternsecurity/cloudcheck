import io
import csv
import logging
import zipfile
import requests
import ipaddress
import traceback
from pathlib import Path
from requests_cache import CachedSession
from requests_cache.backends import SQLiteCache

from .cidr import CidrRanges

log = logging.getLogger("cloudcheck.providers")

db_path = Path.home() / ".cache" / "cloudcheck" / "requests-cache.sqlite"
backend = SQLiteCache(db_path=db_path)
sessions = {}


class CloudProvider:
    main_url = ""
    provider_type = "cloud"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36"
    }

    def __init__(self, cache_for=None):
        if cache_for is None:
            # default = cache IP lists for 7 days
            cache_for = 60 * 60 * 24 * 7
        global sessions
        try:
            self.session = sessions[cache_for]
        except KeyError:
            self.session = CachedSession(expire_after=cache_for, backend=backend)
            sessions[cache_for] = self.session
        self.ranges = CidrRanges(self.get_ranges())

    def get_ranges(self):
        try:
            response = self.session.get(
                self.main_url, allow_redirects=True, verify=False, headers=self.headers
            )
            try:
                return self.parse_response(response)
            except Exception:
                log.warning(f"Error parsing response: {traceback.format_exc()}")
        except requests.RequestException as e:
            log.warning(f"Error retrieving {self.main_url}: {e}")
        return []

    def parse_response(self, response):
        pass

    @classmethod
    @property
    def name(cls):
        return cls.__name__

    def __str__(self):
        return self.name

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


class Cloudflare(CloudProvider):
    main_url = "https://api.cloudflare.com/client/v4/ips"
    provider_type = "cdn"

    def parse_response(self, response):
        ranges = set()
        response_json = response.json()
        for ip_type in ("ipv4_cidrs", "ipv6_cidrs"):
            for ip_range in response_json.get("result", {}).get(ip_type, []):
                ranges.add(ip_range)
        return ranges


class Akamai(CloudProvider):
    main_url = "https://techdocs.akamai.com/property-manager/pdfs/akamai_ipv4_ipv6_CIDRs-txt.zip"
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


class Github(CloudProvider):
    main_url = "https://api.github.com/meta"
    provider_type = "cdn"

    def parse_response(self, response):
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
        return ranges
