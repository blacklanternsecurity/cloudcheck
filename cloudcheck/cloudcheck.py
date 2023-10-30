import sys
import json
import asyncio

from .helpers import CustomJSONEncoder
from .providers import cloud_providers


def check(ip):
    return cloud_providers.check(ip)


async def _main():
    ips = sys.argv[1:]
    if not ips:
        print("usage: cloudcheck 1.2.3.4 [update | [ips...]]")
    elif len(ips) == 1 and ips[0].lower() == "update":
        tasks = [asyncio.create_task(p.update()) for p in cloud_providers]
        await asyncio.gather(*tasks)
        with open(cloud_providers.json_path, "w") as f:
            json.dump(cloud_providers.to_json(), f, sort_keys=True, indent=4, cls=CustomJSONEncoder)
        return
    for ip in ips:
        provider, provider_type, subnet = check(ip)
        if provider:
            print(f"{ip} belongs to {provider} ({provider_type}) ({subnet})")
        else:
            print(f"{ip} is not listed as a cloud resource")


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
