import pytest
import asyncio

from cloudcheck import cloud_providers
from cloudcheck.helpers import domain_parents


@pytest.mark.asyncio
async def test_cloudcheck():
    provider_names = (
        "amazon",
        "google",
        "azure",
        "digitalocean",
        "oracle",
        "akamai",
        "cloudflare",
        "github",
    )
    for provider_name in provider_names:
        assert provider_name in cloud_providers.providers
        provider = cloud_providers.providers[provider_name]
        assert provider.ranges or provider.domains

    google = cloud_providers.providers["google"]
    assert google.domain_match("test.asdf.google") == "google"
    assert google.domain_match("test.asdf.google.asdf") == False

    domain_parents_list = list(domain_parents("asdf.cloud.google.com"))
    assert domain_parents_list == [
        "com",
        "google.com",
        "cloud.google.com",
        "asdf.cloud.google.com",
    ]

    assert cloud_providers.check_host("asdf.google") == ("Google", "cloud", "google")
    assert cloud_providers.check_host("asdf.googles") == (None, None, None)
    assert cloud_providers.check_host("test.amazonaws.com") == (
        "Amazon",
        "cloud",
        "amazonaws.com",
    )

    amazon = cloud_providers.providers["amazon"]
    assert amazon.ranges
    amazon_range = next(iter(amazon.ranges))
    assert cloud_providers.check(amazon_range.broadcast_address) == (
        "Amazon",
        "cloud",
        amazon_range,
    )
    assert cloud_providers.check_ip(amazon_range.broadcast_address) == (
        "Amazon",
        "cloud",
        amazon_range,
    )

    assert cloud_providers.last_updated


if __name__ == "__main__":
    asyncio.run(test_cloudcheck())
