import pytest
from tollbit._apis.content_api import ContentAPI
from tollbit._apis.errors import (
    BadRequestError,
    ServerError,
    UnknownError,
)
from tollbit._apis.models import ContentRate
import requests
from unittest import mock


# --- Mocks and Fixtures ---
class MockResponse:
    def __init__(self, json_obj=None, body_text=None, status_code=200):
        self._json_obj = json_obj or []
        self.body_text = body_text
        self.status_code = status_code

    def json(self):
        return self._json_obj

    @property
    def text(self):
        return self.body_text

    @property
    def headers(self):
        text_type = "application/json" if self._json_obj is not None else "text/plain"
        return {"Content-Type": text_type}

    @property
    def reason(self):
        return self.body_text or "OK"


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
            "cuid": "license-cuid-123",
            "licenseType": "ON_DEMAND",
            "licensePath": "/licenses/standard",
            "permissions": [],
            "validUntil": "2024-12-31T23:59:59Z",
        },
        "error": "",
    }
    patch_requests_get(MockResponse(json_obj=[fake_rate]))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = client.get_rate("example.com/path/to/content")

    requests.get.assert_called_with(
        f"{test_env.developer_api_base_url}/dev/v1/rate/example.com/path/to/content",
        headers={"TollbitKey": "test-secret-key", "User-Agent": "test-agent"},
    )

    assert isinstance(resp, list)
    assert isinstance(resp[0], ContentRate)


def test_get_rate_bad_request(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Bad Request", status_code=400))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(BadRequestError):
        client.get_rate("example.com/path/to/content")


def test_get_rate_server_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Server Error", status_code=500))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        client.get_rate("example.com/path/to/content")


def test_get_rate_unknown_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Teapots on the attack", status_code=418))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(UnknownError):
        client.get_rate("example.com/path/to/content")


def test_get_rate_unreachable(mock_server_down, test_env):
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        client.get_rate("example.com/path/to/content")

# ======= Get Content Catalog Tests =======
def test_get_content_catalog_success(patch_requests_get, test_env):
    fake_catalog = {
        "contents": [
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
    patch_requests_get(MockResponse(json_obj=[fake_catalog]))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = client.get_content_catalog("example.com", page_size=2)

    requests.get.assert_called_with(
        f"{test_env.developer_api_base_url}/dev/v1/content/example.com/catalog/list?pageSize=2",
        headers={"TollbitKey": "test-secret-key", "User-Agent": "test-agent"},
    )

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert resp[0].next_page_token == "next-page-token"
    assert len(resp[0].contents) == 2
    assert resp[0].contents[0].property_id == "content-1"
    assert resp[0].contents[1].property_id == "content-2"


def test_get_content_catalog_second_page(patch_requests_get, test_env):
    fake_catalog = {
        "contents": [
            {
                "propertyId": "content-3",
                "pageUrl": "https://example.com/content-1",
                "lastMod": "2024-01-01T00:00:00Z",
            },
        ],
        "pageToken": None,
    }
    patch_requests_get(MockResponse(json_obj=[fake_catalog]))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = client.get_content_catalog("example.com", page_size=2, page_token="next-page-token")

    requests.get.assert_called_with(
        f"{test_env.developer_api_base_url}/dev/v1/content/example.com/catalog/list?pageSize=2&pageToken=next-page-token",
        headers={"TollbitKey": "test-secret-key", "User-Agent": "test-agent"},
    )

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert resp[0].next_page_token == None
    assert len(resp[0].contents) == 1
    assert resp[0].contents[0].property_id == "content-3"


def test_get_content_catalog_no_page(patch_requests_get, test_env):

    patch_requests_get(MockResponse(json_obj=[]))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    resp = client.get_content_catalog("example.com", page_size=2)

    assert isinstance(resp, list)
    assert len(resp) == 0


def test_get_content_catalog_server_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Server Error", status_code=500))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        client.get_content_catalog("example.com", page_size=2)


def test_get_content_catalog_unknown_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Teapots on the attack", status_code=418))
    client = ContentAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    with pytest.raises(UnknownError):
        client.get_content_catalog("example.com", page_size=2)
