import pytest
from tollbit._apis.content_api import ContentAPI
from tollbit._apis.errors import (
    UnauthorizedError,
    BadRequestError,
    ServerError,
    UnknownError,
)
from tollbit._apis.models import ContentRate
from tollbit.tokens import TollbitToken
import requests
from tollbit._apis.models._hand_rolled.get_content import DeveloperContentResponseSuccess


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


# Patch requests.get for testing
@pytest.fixture()
def patch_requests_get(monkeypatch):
    def _patch_requests_get(response: MockResponse):
        monkeypatch.setattr(requests, "get", lambda url, headers=None: response)

    return _patch_requests_get


@pytest.fixture()
def mock_server_down(monkeypatch):
    def _raise_connection_error(url, headers=None):
        raise requests.ConnectionError("Unable to connect to the server")

    monkeypatch.setattr(requests, "get", _raise_connection_error)


# --- Tests ---
def test_get_rate_success(patch_requests_get, test_env):
    # Simulate a valid ContentRate list response
    fake_rate = {
        "price": {
            "priceMicros": 1000,
            "currency": "USD",
        },
        "license": {
            "licenseType": "ON_DEMAND",
            "licensePath": "/licenses/standard",
            "permissions": [],
            "validUntil": "2024-12-31T23:59:59Z",
        },
        "error": "",
    }
    patch_requests_get(MockResponse(json_obj=[fake_rate]))
    client = ContentAPI(user_agent="test-agent", env=test_env)
    resp = client.get_rate("example.com/path/to/content")
    assert isinstance(resp, list)
    assert isinstance(resp[0], ContentRate)


def test_get_rate_bad_request(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Bad Request", status_code=400))
    client = ContentAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(BadRequestError):
        client.get_rate("example.com/path/to/content")


def test_get_rate_server_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Server Error", status_code=500))
    client = ContentAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        client.get_rate("example.com/path/to/content")


def test_get_rate_unknown_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Teapots on the attack", status_code=418))
    client = ContentAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(UnknownError):
        client.get_rate("example.com/path/to/content")


def test_get_rate_unreachable(mock_server_down, test_env):
    client = ContentAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        client.get_rate("example.com/path/to/content")


def test_get_content_success(patch_requests_get, test_env):

    fake_content = {
        "metadata": {
            "title": "Sample Title",
            "description": "Sample Description",
            "imageUrl": "https://example.com/image.png",
            "author": "Author Name",
            "published": "2024-01-01T00:00:00Z",
            "modified": "2024-01-02T00:00:00Z",
        },
        "content": {
            "header": "<header>Header Content</header>",
            "main": "<main>Main Content</main>",
            "footer": "<footer>Footer Content</footer>",
        },
        "rate": {
            "price": {
                "priceMicros": 0,
                "currency": "USD",
            },
            "license": {
                "cuid": "license-cuid",
                "licenseType": "STANDARD",
                "licensePath": "/licenses/standard",
                "permissions": [],
                "validUntil": "2024-12-31T23:59:59Z",
            },
            "error": "",
        },
    }
    patch_requests_get(MockResponse(json_obj=[fake_content]))
    client = ContentAPI(user_agent="test-agent", env=test_env)
    resp = client.get_content(TollbitToken("dummy-token"), "example.com/path/to/content")
    assert isinstance(resp, list)
    assert isinstance(resp[0], DeveloperContentResponseSuccess)


def test_get_content_bad_token(patch_requests_get, test_env):
    fake_response = [
        {
            "price": {"priceMicros": 1000, "currency": "USD"},
            "license": {
                "cuid": "r6y1oozkapcoyzfm6dgc7813",
                "licenseType": "ON_DEMAND_LICENSE",
                "licensePath": "http://dev-api.tollbit.com/license/b7vrnorhwjg1vgrrr93gijcx/ON_DEMAND_LICENSE_qii52lfti6b5s6b314hu9hpo",
                "permissions": [{"name": "PARTIAL_USE"}],
                "validUntil": "2024-12-13T00:00:21Z",
            },
            "error": "error parsing content token: could not parse jwt when validating content access token: could not parse jwt when validating content access token: error parsing tollbit token: token signature is invalid: crypto/ecdsa: verification error",
        },
        {
            "price": {"priceMicros": 0, "currency": "USD"},
            "license": {
                "cuid": "arims1b01jel3a8pq5t36zz6",
                "licenseType": "ON_DEMAND_FULL_USE_LICENSE",
                "licensePath": "http://dev-api.tollbit.com/license/b7vrnorhwjg1vgrrr93gijcx/ON_DEMAND_FULL_USE_LICENSE_avsuhtj5e6wn0y5dmsah4jkz",
                "permissions": [{"name": "FULL_USE"}, {"name": "PARTIAL_USE"}],
                "validUntil": "2024-12-13T00:00:21Z",
            },
            "error": "error parsing content token: could not parse jwt when validating content access token: could not parse jwt when validating content access token: error parsing tollbit token: token signature is invalid: crypto/ecdsa: verification error",
        },
    ]

    patch_requests_get(MockResponse(json_obj=fake_response))
    client = ContentAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(UnauthorizedError):
        client.get_content(TollbitToken("invalid-token"), "example.com/path/to/content")


@pytest.mark.skip(
    reason="This currently returns an empty object instead of a 404. We need to discuss this for V2"
)
def test_get_content_no_content(patch_requests_get):
    fake_response = [
        {
            "content": {"header": "", "main": "", "footer": ""},
            "metadata": {
                "title": None,
                "description": None,
                "imageUrl": None,
                "author": None,
                "published": None,
                "modified": None,
            },
            "rate": {
                "price": {"priceMicros": 7000, "currency": "USD"},
                "license": {
                    "cuid": "r6y1oozkapcoyzfm6dgc7813",
                    "licenseType": "ON_DEMAND_LICENSE",
                    "licensePath": "http://dev-api.tollbit.com/license/b7vrnorhwjg1vgrrr93gijcx/ON_DEMAND_LICENSE_qii52lfti6b5s6b314hu9hpo",
                    "permissions": [{"name": "PARTIAL_USE"}],
                    "validUntil": "2024-12-13T00:00:21Z",
                },
                "error": "",
            },
        }
    ]

    patch_requests_get(MockResponse(json_obj=fake_response))
    client = ContentAPI(user_agent="test-agent", environment="local")

    with pytest.raises(BadRequestError):
        client.get_content(TollbitToken("dummy-token"), "nosuchurl.com/imaginary")


def test_get_content_server_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Server Error", status_code=500))
    client = ContentAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        client.get_content(TollbitToken("dummy-token"), "example.com/path/to/content")


def test_get_content_unknown_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Teapots on the attack", status_code=418))
    client = ContentAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(UnknownError):
        client.get_content(TollbitToken("dummy-token"), "example.com/path/to/content")


def test_get_content_unreachable(mock_server_down, test_env):
    client = ContentAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        client.get_content(TollbitToken("dummy-token"), "example.com/path/to/content")
