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
        force_refresh=True
    )
    
    with pytest.raises(CloudCheckError, match=r"Failed to fetch cloud provider data from https://invalid\.example\.com/nonexistent\.json after 3 attempts"):
        await cloudcheck.lookup("8.8.8.8")


def test_import_provider():
    from cloudcheck.providers import Amazon

    assert Amazon.regexes
