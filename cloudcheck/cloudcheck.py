import sys
import asyncio
from datetime import datetime

from .providers import cloud_providers


def check(ip):
    return cloud_providers.check(ip)


async def update(cache_hrs=168, force=False):
    time_since_last_update = datetime.now() - cloud_providers.last_updated
    hours_since_last_update = time_since_last_update / 60 / 60
    if force or hours_since_last_update >= cache_hrs:
        await cloud_providers.update()


async def _main():
    ips = sys.argv[1:]
    if not ips:
        print("usage: cloudcheck 1.2.3.4 [update | [ips...]]")
    elif len(ips) == 1 and ips[0].lower() == "update":
        await cloud_providers.update_from_sources()
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
