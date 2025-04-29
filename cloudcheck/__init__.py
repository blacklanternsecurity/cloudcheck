from datetime import datetime

from .providers import cloud_providers  # noqa


def check(ip):
    return cloud_providers.check(ip)


async def update(cache_hrs=168 + 24, force=False):
    time_since_last_update = datetime.now() - cloud_providers.last_updated
    hours_since_last_update = time_since_last_update.total_seconds() / 3600
    if force or hours_since_last_update >= cache_hrs:
        await cloud_providers.update()
