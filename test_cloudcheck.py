import re

import pytest
from cloudcheck import CloudCheck, CloudCheckError


@pytest.mark.asyncio
async def test_lookup_google_dns():
    cloudcheck = CloudCheck()
    results = await cloudcheck.lookup("8.8.8.8")
    names = [provider["name"] for provider in results]
    assert "Google" in names, f"Expected Google in results: {names}"


@pytest.mark.asyncio
async def test_lookup_amazon_domain():
    cloudcheck = CloudCheck()
    results = await cloudcheck.lookup("asdf.amazon.com")
    names = [provider["name"] for provider in results]
    assert "Amazon" in names, f"Expected Amazon in results: {names}"


@pytest.mark.asyncio
async def test_lookup_with_invalid_url():
    """Test that lookup raises RuntimeError with proper message when URL is invalid"""
    cloudcheck = CloudCheck(
        signature_url="https://invalid.example.com/nonexistent.json",
        max_retries=2,
        retry_delay_seconds=0,
        force_refresh=True,
    )

    with pytest.raises(
        CloudCheckError,
        match=r"Failed to fetch cloud provider data from https://invalid\.example\.com/nonexistent\.json after 3 attempts",
    ):
        await cloudcheck.lookup("8.8.8.8")


def test_import_provider():
    from cloudcheck.providers import Amazon

    assert Amazon.regexes


@pytest.mark.parametrize(
    "provider_name,hostname,expected",
    [
        ("Amazon", "mybucket.s3.amazonaws.com", {"name": "mybucket"}),
        (
            "Amazon",
            "mybucket.s3-us-west-2.amazonaws.com",
            {"name": "mybucket", "region": "us-west-2"},
        ),
        (
            "Amazon",
            "mybucket.s3.eu-central-1.amazonaws.com",
            {"name": "mybucket", "region": "eu-central-1"},
        ),
        (
            "DigitalOcean",
            "mybucket.nyc3.digitaloceanspaces.com",
            {"name": "mybucket", "region": "nyc3"},
        ),
        (
            "Hetzner",
            "mybucket.fsn1.your-objectstorage.com",
            {"name": "mybucket", "region": "fsn1"},
        ),
        ("Google", "mybucket.storage.googleapis.com", {"name": "mybucket"}),
        ("Google", "mybucket.firebaseio.com", {"name": "mybucket"}),
        ("Microsoft", "mybucket.blob.core.windows.net", {"name": "mybucket"}),
        ("Cloudflare", "mybucket.r2.dev", {"name": "mybucket"}),
        (
            "Cloudflare",
            "mybucket.r2.cloudflarestorage.com",
            {"name": "mybucket"},
        ),
    ],
)
def test_storage_bucket_hostname_named_groups(provider_name, hostname, expected):
    import cloudcheck.providers as providers

    provider_cls = getattr(providers, provider_name)
    patterns = provider_cls.regexes["STORAGE_BUCKET_HOSTNAME"]
    for pattern in patterns:
        match = re.fullmatch(pattern, hostname)
        if match:
            groups = {k: v for k, v in match.groupdict().items() if v is not None}
            assert groups == expected, (
                f"{provider_name}: {hostname} matched {pattern} but groups={groups}"
            )
            return
    pytest.fail(
        f"{provider_name}: no STORAGE_BUCKET_HOSTNAME pattern matched {hostname}"
    )


def test_all_storage_bucket_regexes_compile():
    from cloudcheck.providers import load_provider_classes

    for provider_cls in load_provider_classes().values():
        regexes = provider_cls.model_fields["regexes"].default or {}
        for category, patterns in regexes.items():
            for pattern in patterns:
                compiled = re.compile(pattern)
                assert "name" in compiled.groupindex, (
                    f"{provider_cls.__name__} {category} pattern {pattern!r} "
                    f"is missing the 'name' named group"
                )
