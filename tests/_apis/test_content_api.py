import json
from datetime import date, datetime, timezone
import pytest
import httpx
from tollbit._apis.content_api import AsyncContentAPI
from tollbit._apis.errors import (
    ServerError,
    ApiError,
)
from tollbit._apis.models import (
    DeveloperRateResponse,
    CatalogResponse,
    BatchRateResponseV2,
    PagedPropertyListResponse,
)
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
        f"{test_env.developer_api_base_url}/dev/v2/rates/example.com/path/to/content"
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
    assert "customLicenseId" not in req_obj.url.params


@pytest.mark.anyio
async def test_get_rate_with_custom_license_ids(respx_mock, test_env):
    fake_rate = {
        "price": {
            "priceMicros": 2000,
            "currency": "USD",
        },
        "license": {
            "id": "custom-license-1",
            "licenseType": "CUSTOM_LICENSE",
            "licensePath": "/licenses/custom",
            "permissions": [],
        },
    }
    route = respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/rates/example.com/path/to/content"
    ).mock(return_value=httpx.Response(200, json=[fake_rate]))
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = await client.get_rate(
        "example.com/path/to/content",
        custom_license_ids=["custom-license-1", "custom-license-2"],
    )
    req_obj = assert_request_made(route)
    assert req_obj.url.params.get_list("customLicenseId") == [
        "custom-license-1",
        "custom-license-2",
    ]
    assert resp[0].license.id == "custom-license-1"


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
        f"{test_env.developer_api_base_url}/dev/v2/rates/example.com/path/to/content"
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
        f"{test_env.developer_api_base_url}/dev/v2/rates/example.com/path/to/content"
    ).mock(return_value=httpx.Response(418, text="Teapots on the attack"))
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        await client.get_rate("example.com/path/to/content")
    error = exc_info.value
    assert str(error) == "API Error: (418) Teapots on the attack"


@pytest.mark.anyio
async def test_get_rate_unreachable(mock_httpx_server_down, test_env):
    mock_httpx_server_down(
        f"{test_env.developer_api_base_url}/dev/v2/rates/example.com/path/to/content"
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        await client.get_rate("example.com/path/to/content")


@pytest.mark.anyio
async def test_get_rates_success(respx_mock, test_env):
    fake_response = [
        {
            "url": "https://example.com/a",
            "rates": [
                {
                    "price": {"priceMicros": 2000, "currency": "USD"},
                    "license": {
                        "cuid": "custom-license-1",
                        "licenseType": "CUSTOM_LICENSE",
                        "licensePath": "/licenses/custom",
                        "permissions": [],
                        "validUntil": "",
                    },
                    "error": "",
                }
            ],
        },
        {"url": "https://example.com/b", "rates": []},
    ]
    route = respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/rates/batch").mock(
        return_value=httpx.Response(200, json=fake_response)
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = await client.get_rates(
        ["https://example.com/a", "https://example.com/b"],
        custom_license_ids=["custom-license-1"],
    )
    req_obj = assert_request_made(route)
    assert json.loads(req_obj.content) == {
        "urls": ["https://example.com/a", "https://example.com/b"],
        "customLicenseIds": ["custom-license-1"],
    }
    assert all(isinstance(r, BatchRateResponseV2) for r in resp)
    assert resp[0].rates[0].license.cuid == "custom-license-1"
    assert resp[1].rates == []


@pytest.mark.anyio
async def test_get_rates_without_custom_license_ids(respx_mock, test_env):
    route = respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/rates/batch").mock(
        return_value=httpx.Response(200, json=[])
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    await client.get_rates(["https://example.com/a"])
    req_obj = assert_request_made(route)
    assert json.loads(req_obj.content) == {"urls": ["https://example.com/a"]}


@pytest.mark.anyio
async def test_get_rates_problem_json_error(respx_mock, test_env):
    fake_response = {
        "detail": "Fail",
        "instance": "/dev/v2/rates/batch",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }
    respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/rates/batch").mock(
        return_value=httpx.Response(
            400, json=fake_response, headers={"Content-Type": "application/problem+json"}
        )
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        await client.get_rates(["https://example.com/a"])
    assert (
        str(exc_info.value) == "API Error: (400) Bad Request - Fail (instance: /dev/v2/rates/batch)"
    )


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
async def test_get_content_catalog_with_modified_dates(respx_mock, test_env):
    route = respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/catalog/list"
    ).mock(return_value=httpx.Response(200, json={"pages": [], "pageToken": None}))
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    await client.get_content_catalog(
        "example.com",
        modified_from=date(2026, 9, 1),
        modified_to=datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc),
    )
    req_obj = assert_request_made(route)
    assert dict(req_obj.url.params) == {
        "pageSize": "100",
        "from": "2026-09-01",
        "to": "2026-09-30T12:00:00+00:00",
    }


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


@pytest.mark.anyio
async def test_list_properties_success(respx_mock, test_env):
    fake_response = {
        "nextToken": "next-page",
        "items": [
            {
                "domain": "example.com",
                "name": "Example",
                "addedAt": "2026-09-01T00:00:00Z",
                "ratesEnabledAt": "2026-09-02T00:00:00Z",
                "readyToLicense": True,
                "licenses": [
                    {
                        "type": "ON_DEMAND_LICENSE",
                        "ratesEnabled": True,
                        "rates": [{"pathPrefix": "/", "priceMicros": 1000, "currency": "USD"}],
                    }
                ],
            }
        ],
    }
    route = respx_mock.get(f"{test_env.developer_api_base_url}/dev/v2/properties").mock(
        return_value=httpx.Response(200, json=fake_response)
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = await client.list_properties(
        page_size=50,
        page_token="this-page",
        ready_to_license=True,
        added_from=date(2026, 9, 1),
        added_to=datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc),
    )
    req_obj = assert_request_made(route)
    assert dict(req_obj.url.params) == {
        "pageSize": "50",
        "pageToken": "this-page",
        "readyToLicense": "true",
        "from": "2026-09-01",
        "to": "2026-09-30T12:00:00+00:00",
    }
    assert isinstance(resp, PagedPropertyListResponse)
    assert resp.next_token == "next-page"
    assert resp.items[0].licenses[0].rates[0].price_micros == 1000


@pytest.mark.anyio
async def test_list_properties_defaults(respx_mock, test_env):
    route = respx_mock.get(f"{test_env.developer_api_base_url}/dev/v2/properties").mock(
        return_value=httpx.Response(200, json={"nextToken": "", "items": []})
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = await client.list_properties()
    req_obj = assert_request_made(route)
    assert dict(req_obj.url.params) == {"pageSize": "100"}
    assert resp.items == []


@pytest.mark.anyio
async def test_list_properties_problem_json_error(respx_mock, test_env):
    fake_response = {
        "detail": "invalid pageSize parameter",
        "instance": "/dev/v2/properties",
        "status": 400,
        "title": "Bad Request",
        "type": "about:blank",
    }
    respx_mock.get(f"{test_env.developer_api_base_url}/dev/v2/properties").mock(
        return_value=httpx.Response(
            400, json=fake_response, headers={"Content-Type": "application/problem+json"}
        )
    )
    client = AsyncContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        await client.list_properties(page_size=5000)
    assert (
        str(exc_info.value)
        == "API Error: (400) Bad Request - invalid pageSize parameter (instance: /dev/v2/properties)"
    )
