import pytest
import httpx
from tollbit._apis.token_api import AsyncTokenAPI
from tollbit._apis.errors import (
    ServerError,
    ApiError,
)
from tollbit._apis.models import (
    CreateSubdomainAccessTokenRequest,
    CreateCrawlAccessTokenRequest,
)
from test_helpers.mock_response import (
    mock_httpx_server_down,
    assert_httpx_request_headers,
    assert_httpx_request_json_body,
    assert_request_made,
)


# --- Tests for Content Access Token ---
@pytest.mark.anyio
async def test_get_content_token_success(respx_mock, test_env):
    token_route = respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/tokens/content").mock(
        return_value=httpx.Response(200, json={"token": "TOKEN-ABC123"})
    )
    client = AsyncTokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateSubdomainAccessTokenRequest(
        url="https://example.com",
        user_agent="test-agent",
        max_price_micros=1000000,
        currency="USD",
        license_type="ON_DEMAND_LICENSE",
        license_cuid="",
    )
    response = await client.get_content_token(req)
    assert response.token == "TOKEN-ABC123"

    raw_request = assert_request_made(token_route)
    assert_httpx_request_headers(
        raw_request,
        {
            "User-Agent": "test-agent",
            "TollbitKey": "test-key",
            "Content-Type": "application/json",
        },
    )

    assert_httpx_request_json_body(
        raw_request,
        {
            "url": "https://example.com/",
            "userAgent": "test-agent",
            "maxPriceMicros": 1000000,
            "currency": "USD",
            "licenseType": "ON_DEMAND_LICENSE",
            "licenseCuid": "",
        },
    )


@pytest.mark.anyio
async def test_get_content_token_problem_json_error(respx_mock, test_env):
    respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/tokens/content").mock(
        return_value=httpx.Response(
            401,
            headers={"Content-Type": "application/problem+json"},
            json={
                "detail": "Invalid API key",
                "instance": "/dev/v2/tokens/content",
                "status": 401,
                "title": "Unauthorized",
                "type": "about:blank",
            },
        )
    )

    client = AsyncTokenAPI(api_key="bad-key", user_agent="test-agent", env=test_env)
    req = CreateSubdomainAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        maxPriceMicros=1000000,
        currency="USD",
        licenseType="ON_DEMAND_LICENSE",
        licenseCuid="",
    )
    with pytest.raises(ApiError) as excinfo:
        await client.get_content_token(req)

    error = excinfo.value
    assert (
        str(error)
        == "API Error: (401) Unauthorized - Invalid API key (instance: /dev/v2/tokens/content)"
    )


@pytest.mark.anyio
async def test_get_content_token_non_problem_json_error(respx_mock, test_env):
    respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/tokens/content").mock(
        return_value=httpx.Response(418, text="Teapots on the attack")
    )

    client = AsyncTokenAPI(api_key="bad-key", user_agent="test-agent", env=test_env)
    req = CreateSubdomainAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        maxPriceMicros=1000000,
        currency="USD",
        licenseType="ON_DEMAND_LICENSE",
        licenseCuid="",
    )
    with pytest.raises(ApiError) as excinfo:
        await client.get_content_token(req)

    error = excinfo.value
    assert str(error) == "API Error: (418) Teapots on the attack"


@pytest.mark.anyio
async def test_get_content_token_unreachable(mock_httpx_server_down, test_env):
    mock_httpx_server_down(f"{test_env.developer_api_base_url}/dev/v2/tokens/content")

    client = AsyncTokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateSubdomainAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        maxPriceMicros=1000000,
        currency="USD",
        licenseType="ON_DEMAND_LICENSE",
        licenseCuid="",
    )

    with pytest.raises(ServerError) as excinfo:
        await client.get_content_token(req)

    assert isinstance(excinfo.value, ServerError)


# # --- Tests for Crawl Access Token ---


@pytest.mark.anyio
async def test_get_crawl_token_success(respx_mock, test_env):
    # patch_requests_post(MockResponse(json_obj={"token": "TOKEN-ABC123"}))
    token_route = respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/tokens/crawl").mock(
        return_value=httpx.Response(200, json={"token": "TOKEN-ABC123"})
    )

    client = AsyncTokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateCrawlAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
    )
    response = await client.get_crawl_token(req)
    assert response.token == "TOKEN-ABC123"

    raw_request = assert_request_made(token_route)
    assert_httpx_request_headers(
        raw_request,
        {
            "User-Agent": "test-agent",
            "TollbitKey": "test-key",
            "Content-Type": "application/json",
        },
    )

    assert_httpx_request_json_body(
        raw_request,
        {
            "url": "https://example.com/",
            "userAgent": "test-agent",
        },
    )


@pytest.mark.anyio
async def test_get_crawl_token_problem_json_error(respx_mock, test_env):
    respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/tokens/crawl").mock(
        return_value=httpx.Response(
            401,
            headers={"Content-Type": "application/problem+json"},
            json={
                "detail": "Invalid API key",
                "instance": "/dev/v2/tokens/content",
                "status": 401,
                "title": "Unauthorized",
                "type": "about:blank",
            },
        )
    )

    client = AsyncTokenAPI(api_key="bad-key", user_agent="test-agent", env=test_env)
    req = CreateCrawlAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
    )
    with pytest.raises(ApiError) as excinfo:
        await client.get_crawl_token(req)

    error = excinfo.value
    assert (
        str(error)
        == "API Error: (401) Unauthorized - Invalid API key (instance: /dev/v2/tokens/content)"
    )


@pytest.mark.anyio
async def test_get_crawl_token_non_problem_json_error(respx_mock, test_env):
    respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/tokens/crawl").mock(
        return_value=httpx.Response(418, text="Teapots on the attack")
    )

    client = AsyncTokenAPI(api_key="bad-key", user_agent="test-agent", env=test_env)
    req = CreateCrawlAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
    )
    with pytest.raises(ApiError) as excinfo:
        await client.get_crawl_token(req)

    error = excinfo.value
    assert str(error) == "API Error: (418) Teapots on the attack"


@pytest.mark.anyio
async def test_get_crawl_token_unreachable(mock_httpx_server_down, test_env):
    mock_httpx_server_down(f"{test_env.developer_api_base_url}/dev/v2/tokens/crawl")

    client = AsyncTokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateCrawlAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
    )

    with pytest.raises(ServerError) as excinfo:
        await client.get_crawl_token(req)

    assert isinstance(excinfo.value, ServerError)
