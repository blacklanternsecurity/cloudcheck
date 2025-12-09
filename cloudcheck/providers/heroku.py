from .base import BaseProvider
from typing import List, Dict


class Heroku(BaseProvider):
    v2fly_company: str = "heroku"
    tags: List[str] = ["cloud"]
