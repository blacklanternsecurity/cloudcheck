import pytest
import asyncio

from cloudcheck import cloud_providers


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
        "zoho",
        "fastly",
    )
    for provider_name in provider_names:
        assert provider_name in cloud_providers.providers
        provider = cloud_providers.providers[provider_name]
        assert provider.ranges or provider.domains or provider.asns

    google = cloud_providers.providers["google"]
    assert google.check("test.asdf.google") == "google"
    assert google.check("test.asdf.google.asdf") == None

    assert cloud_providers.check("asdf.google") == [("Google", "cloud", "google")]
    assert cloud_providers.check("asdf.googles") == []
    assert cloud_providers.check("test.amazonaws.com") == [
        (
            "Amazon",
            "cloud",
            "amazonaws.com",
        )
    ]

    amazon = cloud_providers.providers["amazon"]
    assert amazon.ranges
    amazon_range = next(iter(amazon.ranges))
    assert cloud_providers.check(amazon_range.broadcast_address) == [
        (
            "Amazon",
            "cloud",
            amazon_range,
        )
    ]
    assert cloud_providers.check(amazon_range.broadcast_address) == [
        (
            "Amazon",
            "cloud",
            amazon_range,
        )
    ]

    assert cloud_providers.last_updated

    zoho = cloud_providers.providers["zoho"]
    assert zoho.asns


if __name__ == "__main__":
    asyncio.run(test_cloudcheck())
