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


@pytest.mark.asyncio
async def test_regex_match_amazon_valid():
    cloudcheck = CloudCheck()
    # Test valid bucket name that matches Amazon's STORAGE_BUCKET_NAME pattern
    result = await cloudcheck.regex_match(
        "Amazon", "STORAGE_BUCKET_NAME", "my-bucket-123"
    )
    assert result is True, (
        "Expected 'my-bucket-123' to match Amazon STORAGE_BUCKET_NAME"
    )


@pytest.mark.asyncio
async def test_regex_match_amazon_invalid():
    cloudcheck = CloudCheck()
    # Test invalid bucket name (too short and contains invalid characters)
    result = await cloudcheck.regex_match("Amazon", "STORAGE_BUCKET_NAME", "#my-bucket")
    assert result is False, (
        "Expected '#my-bucket' to not match Amazon STORAGE_BUCKET_NAME"
    )


@pytest.mark.asyncio
async def test_regex_match_nonexistent_provider():
    cloudcheck = CloudCheck()
    # Test with a provider that doesn't exist
    with pytest.raises(ValueError, match="Provider 'NonExistentProvider' not found"):
        await cloudcheck.regex_match(
            "NonExistentProvider", "STORAGE_BUCKET_NAME", "my-bucket"
        )


@pytest.mark.asyncio
async def test_regex_match_nonexistent_regex():
    cloudcheck = CloudCheck()
    # Test with a real provider but non-existent regex name
    with pytest.raises(
        ValueError, match="Regex 'NON_EXISTENT_REGEX' not found for provider 'Amazon'"
    ):
        await cloudcheck.regex_match("Amazon", "NON_EXISTENT_REGEX", "my-bucket")
