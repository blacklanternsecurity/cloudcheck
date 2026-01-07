from cloudcheck.providers.base import BaseProvider
from typing import List


class Gocache(BaseProvider):
    tags: List[str] = ["cdn"]
    short_description: str = "GoCache"
    long_description: str = (
        "A Brazilian content delivery network provider offering CDN services."
    )

    _ips_url = "https://gocache.com.br/ips"
    cidrs: List[str] = [
        "52.67.255.165/32",
        "170.82.175.0/24",
        "187.16.245.192/29",
        "200.189.173.48/28",
        "200.98.28.70/32",
        "187.85.159.176/29",
        "170.84.29.208/29",
        "34.95.168.58/32",
        "140.82.27.226/32",
        "45.77.97.241/32",
        "207.246.123.237/32",
        "207.148.26.195/32",
        "186.211.161.0/29",
        "34.95.213.225/32",
        "34.95.209.169/32",
        "35.247.222.78/32",
        "34.95.253.129/32",
        "34.95.148.131/32",
        "34.95.164.249/32",
        "129.159.48.87/32",
        "200.25.56.64/28",
        "186.211.188.192/28",
        "200.25.49.64/26",
        "150.230.84.126/32",
        "144.22.216.139/32",
        "170.82.172.0/22",
    ]

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        if getattr(response, "status_code", 0) == 200:
            ranges.update(response.text.splitlines())
        return list(ranges)
