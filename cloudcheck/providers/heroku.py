from cloudcheck.providers.base import BaseProvider
from typing import List


class Heroku(BaseProvider):
    v2fly_company: str = "heroku"
    tags: List[str] = ["cloud"]
    short_description: str = "Heroku"
    long_description: str = "A cloud platform as a service that enables developers to build, run, and operate applications entirely in the cloud."
