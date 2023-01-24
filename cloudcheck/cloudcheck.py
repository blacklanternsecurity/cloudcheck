import sys
import json
from datetime import datetime

from .providers import *
from .helpers import ip_network_parents


json_path = Path(__file__).parent.parent / "cloud_providers.json"


class CloudProviders:
    def __init__(self, *args, **kwargs):
        self.providers = dict()
        try:
            with open(json_path) as f:
                self.json = json.load(f)
        except Exception:
            self.json = {}
        provider_classes = CloudProvider.__subclasses__()
        now = datetime.now().isoformat()
        for p in provider_classes:
            provider = p(*args, **kwargs)
            self.providers[provider.name] = provider
            # if we successfully got CIDR ranges, then update the JSON
            if not provider.name in self.json:
                self.json[provider.name] = {}
            json_ranges = self.json[provider.name].get("cidrs", [])
            if provider.ranges.cidrs:
                self.json[provider.name]["last_updated"] = now
                self.json[provider.name]["cidrs"] = sorted(
                    str(r) for r in provider.ranges
                )
            else:
                provider.ranges = CidrRanges(json_ranges)

    def check(self, ip):
        for net in ip_network_parents(ip):
            for provider in self.providers.values():
                if net in provider:
                    return provider.name, net
        return (None, None)

    def __iter__(self):
        yield from self.providers.values()


providers = None


def check(ip):
    global providers
    if providers is None:
        providers = CloudProviders()
    return providers.check(ip)


def refresh_json():
    global providers
    if providers is None:
        providers = CloudProviders()
    with open(json_path, "w") as f:
        json.dump(providers.json, f, sort_keys=True, indent=4)


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
