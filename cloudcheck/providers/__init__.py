import json
import httpx
import asyncio
import logging
import importlib
from pathlib import Path
from datetime import datetime

from .base import BaseCloudProvider
from ..helpers import is_ip, ip_network_parents, CustomJSONEncoder

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
                provider_name = value.__name__
                providers[provider_name] = value


class CloudProviders:
    json_url = "https://raw.githubusercontent.com/blacklanternsecurity/cloudcheck/master/cloud_providers.json"
    json_path = Path(__file__).parent.parent.parent / "cloud_providers.json"

    def __init__(self, httpx_client=None):
        self.now = datetime.now().isoformat()
        self.providers = {}
        self._httpx_client = httpx_client
        self.load_from_json()

    def load_from_json(self):
        if self.json_path.is_file():
            with open(self.json_path) as f:
                try:
                    j = json.load(f)
                except Exception as e:
                    log.warning(f"Failed to parsed JSON at {self.json_path}: {e}")
                    return
                for provider_name, provider_class in providers.items():
                    provider_json = j[provider_name]
                    self.providers[provider_name] = provider_class(
                        provider_json, self.httpx_client
                    )

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
        for provider in self:
            domain = provider.domain_match(host)
            if domain:
                return provider.name, provider.provider_type, domain
        return (None, None, None)

    async def update(self):
        response = await self.httpx_client.get(self.json_url)
        if response:
            with open(self.json_path, "wb") as f:
                f.write(response.content)
            self.load_from_json()
        else:
            log.warning(
                f"Failed to retrieve update from {self.json_url} (response: {response})"
            )

    async def update_from_sources(self):
        tasks = [asyncio.create_task(p.update()) for p in self]
        await asyncio.gather(*tasks)
        with open(self.json_path, "w") as f:
            json.dump(
                self.to_json(), f, sort_keys=True, indent=4, cls=CustomJSONEncoder
            )

    def to_json(self):
        return {n: p.to_json() for n, p in self.providers.items()}

    @property
    def last_updated(self):
        return max([p.last_updated for p in self])

    @property
    def httpx_client(self):
        if self._httpx_client is None:
            self._httpx_client = httpx.AsyncClient(verify=False)
        return self._httpx_client

    def __iter__(self):
        yield from self.providers.values()


cloud_providers = CloudProviders()
