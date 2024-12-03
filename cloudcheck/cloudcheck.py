import sys
import asyncio

from cloudcheck import check
from cloudcheck.providers import cloud_providers


async def _main():
    ips = sys.argv[1:]
    if not ips:
        print("usage: cloudcheck 1.2.3.4 [update | forceupdate | [ips...] | [domains...]]")
    elif len(ips) == 1 and ips[0].lower() == "update":
        await cloud_providers.update()
        return
    elif len(ips) == 1 and ips[0].lower() == "forceupdate":
        await cloud_providers.update_from_sources()
        return
    for ip in ips:
        _provider = False
        for provider, provider_type, subnet in check(ip):
            if provider:
                _provider = True
                print(f"{ip} belongs to {provider} ({provider_type}) ({subnet})")
        if not _provider:
            print(f"{ip} is not listed as a cloud resource")


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
