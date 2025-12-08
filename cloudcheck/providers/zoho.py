from .base import BaseProvider
from typing import List, Dict


class Zoho(BaseProvider):
    v2fly_company: str = ""
    # domains = ["zoho.com", "zoho.com.au", "zoho.eu", "zoho.in", "zohocdn.com", "zohomeetups.com", "zohomerchandise.com", "zohopublic.com", "zohoschools.com", "zohostatic.com", "zohostatic.in", "zohouniversity.com", "zohowebstatic.com"]
    # asns = [2639]
    tags: List[str] = ["cloud"]
    org_ids: List[str] = []

