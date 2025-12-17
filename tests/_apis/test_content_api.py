import pytest
from tollbit._apis.content_api import ContentAPI
from tollbit._apis.errors import (
    BadRequestError,
    ServerError,
    UnknownError,
    ApiError,
)
from tollbit._apis.models import DeveloperRateResponse, CatalogResponse
import requests
from unittest import mock
from test_helpers.mock_response import MockResponse


# Patch requests.get for testing
@pytest.fixture()
def patch_requests_get(monkeypatch):
    def _patch_requests_get(response: MockResponse):
        mock_get = mock.Mock(return_value=response)
        monkeypatch.setattr(requests, "get", mock_get)
        return mock_get

    return _patch_requests_get


@pytest.fixture()
def mock_server_down(monkeypatch):
    def _raise_connection_error(url, headers=None):
        raise requests.ConnectionError("Unable to connect to the server")

    monkeypatch.setattr(requests, "get", _raise_connection_error)


# --- Tests ---
# ======= Get Rate Tests =======
def test_get_rate_success(patch_requests_get, test_env):
    # Simulate a valid ContentRate list response
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
    patch_requests_get(MockResponse(json_obj=[fake_rate]))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = client.get_rate("example.com/path/to/content")

    requests.get.assert_called_with(
        f"{test_env.developer_api_base_url}/dev/v2/rate/example.com/path/to/content",
        headers={"TollbitKey": "test-secret-key", "User-Agent": "test-agent"},
    )

    assert isinstance(resp, list)
    assert isinstance(resp[0], DeveloperRateResponse)


def test_get_rate_problem_json_error(patch_requests_get, test_env):
    fake_response = {
        "detail": "Fail",
        "instance": "/dev/v2/content/pioneervalleygazette.com/daydream",
        "status": 500,
        "title": "Internal Server Error",
        "type": "about:blank",
    }

    patch_requests_get(MockResponse(problem_json_obj=fake_response, status_code=500))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        client.get_rate("example.com/path/to/content")

    error = exc_info.value
    assert (
        str(error)
        == "API Error: (500) Internal Server Error - Fail (instance: /dev/v2/content/pioneervalleygazette.com/daydream)"
    )


def test_get_rate_non_problem_json_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Teapots on the attack", status_code=418))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        client.get_rate("example.com/path/to/content")

    error = exc_info.value
    assert str(error) == "API Error: (418) Teapots on the attack"


def test_get_rate_unreachable(mock_server_down, test_env):
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        client.get_rate("example.com/path/to/content")


# ======= Get Content Catalog Tests =======
def test_get_content_catalog_success(patch_requests_get, test_env):
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
    patch_requests_get(MockResponse(json_obj=fake_catalog))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = client.get_content_catalog("example.com", page_size=2)

    requests.get.assert_called_with(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/catalog/list?pageSize=2",
        headers={"TollbitKey": "test-secret-key", "User-Agent": "test-agent"},
    )

    assert isinstance(resp, CatalogResponse)
    assert resp.pageToken == "next-page-token"
    assert len(resp.pages) == 2
    assert resp.pages[0].propertyId == "content-1"
    assert resp.pages[1].propertyId == "content-2"


def test_get_content_catalog_second_page(patch_requests_get, test_env):
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
    patch_requests_get(MockResponse(json_obj=fake_catalog))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = client.get_content_catalog("example.com", page_size=2, page_token="next-page-token")

    requests.get.assert_called_with(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/catalog/list?pageSize=2&pageToken=next-page-token",
        headers={"TollbitKey": "test-secret-key", "User-Agent": "test-agent"},
    )

    assert isinstance(resp, CatalogResponse)
    assert resp.pageToken is None
    assert len(resp.pages) == 1
    assert resp.pages[0].propertyId == "content-3"


def test_get_content_catalog_problem_json_error(patch_requests_get, test_env):
    fake_response = {
        "detail": "Fail",
        "instance": "/dev/v2/content/pioneervalleygazette.com/daydream",
        "status": 500,
        "title": "Internal Server Error",
        "type": "about:blank",
    }

    patch_requests_get(MockResponse(problem_json_obj=fake_response, status_code=500))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        client.get_content_catalog("example.com", page_size=2)

    error = exc_info.value
    assert (
        str(error)
        == "API Error: (500) Internal Server Error - Fail (instance: /dev/v2/content/pioneervalleygazette.com/daydream)"
    )


def test_get_content_catalog_non_problem_json_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Teapots on the attack", status_code=418))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        client.get_content_catalog("example.com", page_size=2)

    error = exc_info.value
    assert str(error) == "API Error: (418) Teapots on the attack"


def test_get_content_catalog_unreachable(mock_server_down, test_env):
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        client.get_content_catalog("example.com", page_size=2)
