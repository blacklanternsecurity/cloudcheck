import json
import httpx
import pickle
import asyncio
import logging
import importlib
from pathlib import Path
from contextlib import suppress
from datetime import datetime, timedelta

from .base import BaseCloudProvider
from ..helpers import CustomJSONEncoder, make_ip_type

log = logging.getLogger("cloudcheck.providers")

code_path = Path(__file__).parent.parent.parent

# dynamically load cloud provider modules
providers = {}
for file in Path(__file__).parent.glob("*.py"):
    if not file.stem in ("base", "__init__"):
        import_path = f"cloudcheck.providers.{file.stem}"
        module_variables = importlib.import_module(import_path, "cloudcheck")
        for variable in module_variables.__dict__.keys():
            value = getattr(module_variables, variable)
            if hasattr(value, "__mro__") and not value == BaseCloudProvider and BaseCloudProvider in value.__mro__:
                provider_name = value.__name__.lower()
                providers[provider_name] = value


class CloudProviders:
    json_url = "https://raw.githubusercontent.com/blacklanternsecurity/cloudcheck/master/cloud_providers.json"
    json_path = code_path / "cloud_providers.json"
    cache_path = code_path / ".cloudcheck_cache"

    def __init__(self):
        self.providers = {}
        self.cache_key = None
        self.load_from_json()

    def load_from_json(self, force=False):
        # loading from a pickled cache is about 1 second faster than loading from JSON
        # if (not force) and self.cache_path.is_file():
        #     self.load_from_cache()
        # else:
        if self.json_path.is_file():
            with open(self.json_path) as f:
                try:
                    j = json.load(f)
                    for k in list(j):
                        j[k.lower()] = j.pop(k)
                except Exception as e:
                    log.warning(f"Failed to parse JSON at {self.json_path}: {e}")
                    return
                for provider_name, provider_class in providers.items():
                    provider_name = provider_name.lower()
                    provider_json = j.get(provider_name, {})
                    self.providers[provider_name] = provider_class(provider_json)
                self.cache_key = self.json_path.stat()
        else:
            for provider_name, provider_class in providers.items():
                provider_name = provider_name.lower()
                self.providers[provider_name] = provider_class(None)
        # self.write_cache()

    # def load_from_cache(self):
    #     with open(self.cache_path, "rb") as f:
    #         try:
    #             self.providers = pickle.load(f)
    #         except Exception as e:
    #             with suppress(Exception):
    #                 self.cache_path.unlink()
    #             log.warning(
    #                 f"Failed to load cloudcheck cache at {self.cache_path}: {e}"
    #             )

    # def write_cache(self):
    #     with open(self.cache_path, "wb") as f:
    #         try:
    #             pickle.dump(self.providers, f)
    #         except Exception as e:
    #             log.warning(
    #                 f"Failed to write cloudcheck cache to {self.cache_path}: {e}"
    #             )

    def check(self, host):
        host = make_ip_type(host)
        results = []
        for provider in self:
            result = provider.check(host)
            if result is not None:
                results.append((provider.name, provider.provider_type, result))
        return results

    async def update(self, days=1, force=False):
        response, error = None, None
        delta = timedelta(days=days)
        oldest_allowed = datetime.now() - delta
        if self.last_updated > oldest_allowed and not force:
            return
        try:
            async with httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(verify=False)) as client:
                response = await client.get(self.json_url)
        except Exception as e:
            error = e
        if response is not None and response.status_code == 200 and response.content:
            with open(self.json_path, "wb") as f:
                f.write(response.content)
            self.load_from_json(force=True)
            for provider in self:
                provider.radix.defrag()
        else:
            log.warning(f"Failed to retrieve update from {self.json_url} (response: {response}, error: {error})")

    async def update_from_sources(self):
        tasks = [asyncio.create_task(p.update()) for p in self]
        await asyncio.gather(*tasks)
        j = self.to_json()
        if j:
            with open(self.json_path, "w") as f:
                json.dump(self.to_json(), f, sort_keys=True, indent=1, cls=CustomJSONEncoder)
            self.load_from_json(force=True)

    def to_json(self):
        d = {}
        for n, p in self.providers.items():
            d[p.name] = p.to_json()
        return d

    @property
    def last_updated(self):
        if self:
            return max([p.last_updated for p in self])
        else:
            return datetime.min

    def __iter__(self):
        yield from self.providers.values()

    def __bool__(self):
        return bool(list(self))


cloud_providers = CloudProviders()
