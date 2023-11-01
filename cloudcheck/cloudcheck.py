import sys
import asyncio

from cloudcheck import check
from cloudcheck.providers import cloud_providers


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
