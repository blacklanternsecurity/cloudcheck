from cloudcheck.providers.base import BaseProvider
from typing import List


class Heroku(BaseProvider):
    v2fly_company: str = "heroku"
    tags: List[str] = ["cloud"]
