import pytest
from tollbit._apis.content_retrieval_api import ContentRetrievalAPI
from tollbit._apis.errors import (
    BadRequestError,
    ServerError,
    ApiError,
)
from tollbit.tokens import TollbitToken
import requests
from tollbit._apis.models import GetContentResponse
from unittest import mock
from tollbit.content_formats import Format
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
# ======= Get Content Tests =======
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
            "body": "<main>Main Content</main>",
            "footer": "<footer>Footer Content</footer>",
        },
        "rate": {
            "price": {
                "priceMicros": 0,
                "currency": "USD",
            },
            "license": {
                "id": "license-cuid",
                "licenseType": "STANDARD",
                "licensePath": "/licenses/standard",
                "permissions": [],
            },
        },
    }
    patch_requests_get(MockResponse(json_obj=fake_content))
    client = ContentRetrievalAPI(user_agent="test-agent", env=test_env)
    resp = client.get_content(
        TollbitToken("dummy-token"), "example.com/path/to/content", Format.html
    )
    assert isinstance(resp, GetContentResponse)


# https://linear.app/tollbit/issue/TOL-1184/getcontent-v2-returns-empty-response-for-no-content
@pytest.mark.skip(
    reason="This currently returns an empty object instead of a 404. We need to discuss this for V2"
)
def test_get_content_no_content(patch_requests_get):
    fake_response = {
        "content": {"header": "", "body": "", "footer": ""},
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
        },
    }

    patch_requests_get(MockResponse(json_obj=fake_response))
    client = ContentRetrievalAPI(user_agent="test-agent", environment="local")

    with pytest.raises(BadRequestError):
        client.get_content(TollbitToken("dummy-token"), "nosuchurl.com/imaginary", Format.html)


def test_get_content_problem_json_error(patch_requests_get, test_env):
    fake_response = {
        "detail": "Fail",
        "instance": "/dev/v2/content/pioneervalleygazette.com/daydream",
        "status": 500,
        "title": "Internal Server Error",
        "type": "about:blank",
    }

    patch_requests_get(MockResponse(problem_json_obj=fake_response, status_code=500))
    client = ContentRetrievalAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        client.get_content(TollbitToken("dummy-token"), "example.com/path/to/content", Format.html)

    error = exc_info.value
    assert (
        str(error)
        == "API Error: (500) Internal Server Error - Fail (instance: /dev/v2/content/pioneervalleygazette.com/daydream)"
    )


def test_get_content_non_problem_json_error(patch_requests_get, test_env):
    patch_requests_get(MockResponse(body_text="Teapots on the attack", status_code=418))
    client = ContentRetrievalAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        client.get_content(TollbitToken("dummy-token"), "example.com/path/to/content", Format.html)

    error = exc_info.value
    assert str(error) == "API Error: (418) Teapots on the attack"


def test_get_content_unreachable(mock_server_down, test_env):
    client = ContentRetrievalAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        client.get_content(TollbitToken("dummy-token"), "example.com/path/to/content", Format.html)
