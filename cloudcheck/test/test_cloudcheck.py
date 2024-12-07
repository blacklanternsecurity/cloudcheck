import os
import sys
import pytest
import asyncio

from cloudcheck import cloud_providers


@pytest.mark.asyncio
async def test_cloudcheck():
    provider_names = (
        "akamai",
        "amazon",
        "arvancloud",
        "azure",
        "cloudflare",
        "cloudfront",
        "digitalocean",
        "fastly",
        "github",
        "google",
        "hetzner",
        "imperva",
        "oracle",
        "zoho",
    )
    for provider_name in provider_names:
        assert provider_name in cloud_providers.providers
        provider = cloud_providers.providers[provider_name]
        assert provider.ranges or provider.domains or provider.asns

    google = cloud_providers.providers["google"]
    assert google.check("test.asdf.google") == "google"
    assert google.check("test.asdf.google.asdf") is None

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
    zoho = cloud_providers.providers["zoho"]
    assert zoho.ranges

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


@pytest.mark.asyncio
async def test_cloudcheck_cli(monkeypatch, capsys):
    from cloudcheck.cloudcheck import _main

    monkeypatch.setattr(sys, "exit", lambda *args, **kwargs: True)
    monkeypatch.setattr(os, "_exit", lambda *args, **kwargs: True)

    # show version
    monkeypatch.setattr("sys.argv", ["cloudcheck", "azure.com"])
    await _main()
    out, err = capsys.readouterr()
    assert out == "azure.com belongs to Azure (cloud) (azure.com)\n"


if __name__ == "__main__":
    asyncio.run(test_cloudcheck())
