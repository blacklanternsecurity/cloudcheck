import json
import httpx
import asyncio
import logging
import importlib
from pathlib import Path
from datetime import datetime, timedelta

from .base import BaseCloudProvider
from ..helpers import is_ip, ip_network_parents, domain_parents, CustomJSONEncoder

log = logging.getLogger("cloudcheck.providers")

# dynamically load cloud provider modules
providers = {}
for file in Path(__file__).parent.glob("*.py"):
    if not file.stem in ("base", "__init__"):
        import_path = f"cloudcheck.providers.{file.stem}"
        module_variables = importlib.import_module(import_path, "cloudcheck")
        for variable in module_variables.__dict__.keys():
            value = getattr(module_variables, variable)
            if (
                hasattr(value, "__mro__")
                and not value == BaseCloudProvider
                and BaseCloudProvider in value.__mro__
            ):
                provider_name = value.__name__.lower()
                providers[provider_name] = value


class CloudProviders:
    json_url = "https://raw.githubusercontent.com/blacklanternsecurity/cloudcheck/master/cloud_providers.json"
    json_path = Path(__file__).parent.parent.parent / "cloud_providers.json"

    def __init__(self, httpx_client=None):
        self.providers = {}
        self._httpx_client = httpx_client
        self.load_from_json()

    def load_from_json(self):
        if self.json_path.is_file():
            with open(self.json_path) as f:
                try:
                    j = json.load(f)
                    for k in list(j):
                        j[k.lower()] = j.pop(k)
                except Exception as e:
                    log.warning(f"Failed to parsed JSON at {self.json_path}: {e}")
                    return
                for provider_name, provider_class in providers.items():
                    provider_name = provider_name.lower()
                    provider_json = j.get(provider_name, {})
                    self.providers[provider_name] = provider_class(
                        provider_json, self.httpx_client
                    )
        else:
            for provider_name, provider_class in providers.items():
                provider_name = provider_name.lower()
                self.providers[provider_name] = provider_class(None, self.httpx_client)

    def check(self, host):
        if is_ip(host):
            return self.check_ip(host)
        return self.check_host(host)

    def check_ip(self, ip):
        for net in ip_network_parents(ip):
            for provider in self:
                if net in provider:
                    return provider.name, provider.provider_type, net
        return (None, None, None)

    def check_host(self, host):
        for domain_parent in domain_parents(host):
            for provider in self:
                if domain_parent in provider.domains:
                    return provider.name, provider.provider_type, domain_parent
        return (None, None, None)

    async def update(self, days=1, force=False):
        response, error = None, None
        delta = timedelta(days=days)
        oldest_allowed = datetime.now() - delta
        if self.last_updated > oldest_allowed and not force:
            return
        try:
            response = await self.httpx_client.get(self.json_url)
        except Exception as e:
            error = e
        if response is not None and response.status_code == 200 and response.content:
            with open(self.json_path, "wb") as f:
                f.write(response.content)
            self.load_from_json()
        else:
            log.warning(
                f"Failed to retrieve update from {self.json_url} (response: {response}, error: {error})"
            )

    async def update_from_sources(self):
        tasks = [asyncio.create_task(p.update()) for p in self]
        await asyncio.gather(*tasks)
        j = self.to_json()
        if j:
            with open(self.json_path, "w") as f:
                json.dump(
                    self.to_json(), f, sort_keys=True, indent=4, cls=CustomJSONEncoder
                )
            self.load_from_json()

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

    @property
    def httpx_client(self):
        if self._httpx_client is None:
            self._httpx_client = httpx.AsyncClient(verify=False)
        return self._httpx_client

    def __iter__(self):
        yield from self.providers.values()

    def __bool__(self):
        return bool(list(self))


cloud_providers = CloudProviders()
