import pytest
import httpx
from tollbit._apis.content_api import AsyncContentAPI
from tollbit._apis.errors import (
    ServerError,
    ApiError,
)
from tollbit._apis.models import DeveloperRateResponse, CatalogResponse
from test_helpers.mock_response import (
    assert_request_made,
    assert_httpx_request_headers,
    mock_httpx_server_down,
)


# --- Tests ---
# ======= Get Rate Tests =======
@pytest.mark.anyio
async def test_get_rate_success(respx_mock, test_env):
    fake_rate = {
        "price": {
            "priceMicros": 1000,
            "currency": "USD",
        },
        "license": {
            "id": "license-cuid-123",
            "licenseType": "ON_DEMAND",
            "licensePath": "/licenses/standard",
            "permissions": [],
        },
        "error": "",
    }
    route = respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/rate/example.com/path/to/content"
    ).mock(return_value=httpx.Response(200, json=[fake_rate]))
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = await client.get_rate("example.com/path/to/content")
    req_obj = assert_request_made(route)
    assert_httpx_request_headers(
        req_obj,
        {
            "TollbitKey": "test-secret-key",
            "User-Agent": "test-agent",
            "Content-Type": "application/json",
        },
    )
    assert isinstance(resp, list)
    assert isinstance(resp[0], DeveloperRateResponse)


@pytest.mark.anyio
async def test_get_rate_problem_json_error(respx_mock, test_env):
    fake_response = {
        "detail": "Fail",
        "instance": "/dev/v2/content/pioneervalleygazette.com/daydream",
        "status": 500,
        "title": "Internal Server Error",
        "type": "about:blank",
    }
    respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/rate/example.com/path/to/content"
    ).mock(
        return_value=httpx.Response(
            500, json=fake_response, headers={"Content-Type": "application/problem+json"}
        )
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        await client.get_rate("example.com/path/to/content")
    error = exc_info.value
    assert (
        str(error)
        == "API Error: (500) Internal Server Error - Fail (instance: /dev/v2/content/pioneervalleygazette.com/daydream)"
    )


@pytest.mark.anyio
async def test_get_rate_non_problem_json_error(respx_mock, test_env):
    respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/rate/example.com/path/to/content"
    ).mock(return_value=httpx.Response(418, text="Teapots on the attack"))
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        await client.get_rate("example.com/path/to/content")
    error = exc_info.value
    assert str(error) == "API Error: (418) Teapots on the attack"


@pytest.mark.anyio
async def test_get_rate_unreachable(mock_httpx_server_down, test_env):
    mock_httpx_server_down(
        f"{test_env.developer_api_base_url}/dev/v2/rate/example.com/path/to/content"
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        await client.get_rate("example.com/path/to/content")


@pytest.mark.anyio
async def test_get_content_catalog_success(respx_mock, test_env):
    fake_catalog = {
        "pages": [
            {
                "propertyId": "content-1",
                "pageUrl": "https://example.com/content-1",
                "lastMod": "2024-01-01T00:00:00Z",
            },
            {
                "propertyId": "content-2",
                "pageUrl": "https://example.com/content-2",
                "lastMod": None,
            },
        ],
        "pageToken": "next-page-token",
    }
    route = respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/catalog/list"
    ).mock(return_value=httpx.Response(200, json=fake_catalog))
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = await client.get_content_catalog("example.com", page_size=2)
    req_obj = assert_request_made(route)
    assert_httpx_request_headers(
        req_obj,
        {
            "TollbitKey": "test-secret-key",
            "User-Agent": "test-agent",
            "Content-Type": "application/json",
        },
    )
    # Check query params
    assert req_obj.url.params["pageSize"] == "2"
    assert isinstance(resp, CatalogResponse)
    assert resp.page_token == "next-page-token"
    assert len(resp.pages) == 2
    assert resp.pages[0].property_id == "content-1"
    assert resp.pages[1].property_id == "content-2"


@pytest.mark.anyio
async def test_get_content_catalog_second_page(respx_mock, test_env):
    fake_catalog = {
        "pages": [
            {
                "propertyId": "content-3",
                "pageUrl": "https://example.com/content-1",
                "lastMod": "2024-01-01T00:00:00Z",
            },
        ],
        "pageToken": None,
    }
    route = respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/catalog/list"
    ).mock(return_value=httpx.Response(200, json=fake_catalog))
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = await client.get_content_catalog(
        "example.com", page_size=2, page_token="next-page-token"
    )
    req_obj = assert_request_made(route)
    assert req_obj.url.params["pageSize"] == "2"
    assert req_obj.url.params["pageToken"] == "next-page-token"
    assert isinstance(resp, CatalogResponse)
    assert resp.page_token is None
    assert len(resp.pages) == 1
    assert resp.pages[0].property_id == "content-3"


@pytest.mark.anyio
async def test_get_content_catalog_problem_json_error(respx_mock, test_env):
    fake_response = {
        "detail": "Fail",
        "instance": "/dev/v2/content/pioneervalleygazette.com/daydream",
        "status": 500,
        "title": "Internal Server Error",
        "type": "about:blank",
    }
    respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/catalog/list"
    ).mock(
        return_value=httpx.Response(
            500, json=fake_response, headers={"Content-Type": "application/problem+json"}
        )
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        await client.get_content_catalog("example.com", page_size=2)
    error = exc_info.value
    assert (
        str(error)
        == "API Error: (500) Internal Server Error - Fail (instance: /dev/v2/content/pioneervalleygazette.com/daydream)"
    )


@pytest.mark.anyio
async def test_get_content_catalog_non_problem_json_error(respx_mock, test_env):
    respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/catalog/list"
    ).mock(return_value=httpx.Response(418, text="Teapots on the attack"))
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        await client.get_content_catalog("example.com", page_size=2)
    error = exc_info.value
    assert str(error) == "API Error: (418) Teapots on the attack"


@pytest.mark.anyio
async def test_get_content_catalog_unreachable(mock_httpx_server_down, test_env):
    mock_httpx_server_down(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/catalog/list"
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        await client.get_content_catalog("example.com", page_size=2)
