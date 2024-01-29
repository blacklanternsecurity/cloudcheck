from .base import BaseCloudProvider


class Zoho(BaseCloudProvider):
    domains = [
        "zoho.com",
        "zoho.com.au",
        "zoho.eu",
        "zoho.in",
        "zohocdn.com",
        "zohomeetups.com",
        "zohomerchandise.com",
        "zohopublic.com",
        "zohoschools.com",
        "zohostatic.com",
        "zohostatic.in",
        "zohouniversity.com",
        "zohowebstatic.com",
    ]
    asns = [
        2639,
    ]
    provider_type = "cloud"
