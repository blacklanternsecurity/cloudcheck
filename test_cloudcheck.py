import pytest
from cloudcheck import CloudCheck


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


def test_import_provider():
    from cloudcheck.providers import Amazon

    assert Amazon.regexes
