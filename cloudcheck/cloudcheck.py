import sys
import json
from datetime import datetime

from .providers import *
from .helpers import ip_network_parents


class CloudProviders:
    def __init__(self, *args, **kwargs):
        self.providers = dict()
        provider_classes = CloudProvider.__subclasses__()
        for p in provider_classes:
            provider = p(*args, **kwargs)
            self.providers[provider.name] = provider

    def check(self, ip):
        for net in ip_network_parents(ip):
            for provider in self.providers.values():
                if net in provider:
                    return provider.name, net
        return (None, None)

    def json(self):
        j = {}
        for n, p in self.providers.items():
            j[n] = [str(i) for i in p.ranges.cidrs]
        return j

    def __iter__(self):
        yield from self.providers.values()


providers = None


def check(ip):
    global providers
    if providers is None:
        providers = CloudProviders()
    return providers.check(ip)


json_path = Path(__file__).parent.parent / "cloud_providers.json"


def refresh_json():
    global providers
    if providers is None:
        providers = CloudProviders()
    now = datetime.now().isoformat()
    try:
        with open(json_path) as f:
            providers_json = json.loads(f)
    except Exception:
        providers_json = {}
    for provider in providers:
        if not provider.name in providers_json:
            providers_json[provider.name] = {}
        if provider.ranges.cidrs:
            providers_json[provider.name]["last_updated"] = now
            providers_json[provider.name]["cidrs"] = sorted(
                str(r) for r in provider.ranges.cidrs
            )
    with open(json_path, "w") as f:
        f.write(json.dumps(providers_json, sort_keys=True, indent=4))


def main():
    ips = sys.argv[1:]
    if not ips:
        print("usage: cloudcheck 1.2.3.4 [refresh_json | [ips...]]")
    elif len(ips) == 1 and ips[0].lower() == "refresh_json":
        refresh_json()
        return
    for ip in ips:
        provider, subnet = check(ip)
        if provider:
            print(f"{ip} belongs to {provider} ({subnet})")
        else:
            print(f"{ip} is not listed as a cloud resource")


if __name__ == "__main__":
    main()
