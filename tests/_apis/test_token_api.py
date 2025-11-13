import pytest
import json
from tollbit._apis.token_api import TokenAPI
from tollbit._apis.errors import (
    UnauthorizedError,
    BadRequestError,
    ServerError,
    UnknownError,
)
from tollbit._apis.models import (
    CreateSubdomainAccessTokenRequest,
    CreateCrawlAccessTokenRequest,
    Format,
)
from tollbit._environment import Environment
import os

# --- Mocks and Fixtures ---
# Patch requests.post for testing
import requests


class MockResponse:
    def __init__(self, json_obj={}, body_text=None, status_code=200):
        self.json_obj = json_obj
        self.body_text = body_text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("HTTP Error")

    def json(self):
        if not self.json_obj:
            raise RuntimeError("No JSON content")
        return self.json_obj

    def text(self):
        return self.body_text


@pytest.fixture()
def patch_requests_post(monkeypatch):
    def _patch_requests_post(response: MockResponse):
        monkeypatch.setattr(requests, "post", lambda url, headers=None, json=None: response)

    return _patch_requests_post


@pytest.fixture()
def mock_server_down(monkeypatch):
    def _raise_connection_error(url, headers=None, json=None):
        raise requests.ConnectionError("Unable to connect to the server")

    monkeypatch.setattr(requests, "post", _raise_connection_error)


# --- Tests for Content Access Token ---


def test_get_content_token_success(patch_requests_post, test_env):
    patch_requests_post(MockResponse(json_obj={"token": "TOKEN-ABC123"}))
    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateSubdomainAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        maxPriceMicros=1000000,
        currency="USD",
        licenseType="ON_DEMAND_LICENSE",
        licenseCuid="",
        format=Format.markdown,
    )
    response = client.get_content_token(req)
    assert response.token == "TOKEN-ABC123"


def test_get_content_token_bad_api_key(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Invalid API key", status_code=401))
    client = TokenAPI(api_key="bad-key", user_agent="test-agent", env=test_env)

    req = CreateSubdomainAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        maxPriceMicros=1000000,
        currency="USD",
        licenseType="ON_DEMAND_LICENSE",
        licenseCuid="",
        format=Format.markdown,
    )
    with pytest.raises(Exception) as excinfo:
        client.get_content_token(req)

    assert isinstance(excinfo.value, UnauthorizedError)


def test_get_content_token_unauthorized_host(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Bad Request", status_code=400))

    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateSubdomainAccessTokenRequest(
        url="https://nosuchurl.com",
        userAgent="test-agent",
        maxPriceMicros=1000000,
        currency="USD",
        licenseType="ON_DEMAND_LICENSE",
        licenseCuid="",
        format=Format.markdown,
    )

    with pytest.raises(Exception) as excinfo:
        client.get_content_token(req)
    assert isinstance(excinfo.value, BadRequestError)


def test_get_content_token_server_error(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Server Error", status_code=500))

    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateSubdomainAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        maxPriceMicros=1000000,
        currency="USD",
        licenseType="ON_DEMAND_LICENSE",
        licenseCuid="",
        format=Format.markdown,
    )
    with pytest.raises(Exception) as excinfo:
        client.get_content_token(req)
    assert isinstance(excinfo.value, ServerError)


def test_get_content_token_unknown_error(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Teapots on the attack", status_code=418))

    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateSubdomainAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        maxPriceMicros=1000000,
        currency="USD",
        licenseType="ON_DEMAND_LICENSE",
        licenseCuid="",
        format=Format.markdown,
    )
    with pytest.raises(Exception) as excinfo:
        client.get_content_token(req)
    assert isinstance(excinfo.value, UnknownError)


def test_get_content_token_unreachable(mock_server_down, test_env):
    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateSubdomainAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        maxPriceMicros=1000000,
        currency="USD",
        licenseType="ON_DEMAND_LICENSE",
        licenseCuid="",
        format=Format.markdown,
    )

    with pytest.raises(Exception) as excinfo:
        client.get_content_token(req)

    assert isinstance(excinfo.value, ServerError)


# --- Tests for Crawl Access Token ---


def test_get_crawl_token_success(patch_requests_post, test_env):
    patch_requests_post(MockResponse(json_obj={"token": "TOKEN-ABC123"}))
    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateCrawlAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        format=Format.markdown,
    )
    response = client.get_crawl_token(req)
    assert response.token == "TOKEN-ABC123"


def test_get_crawl_token_bad_api_key(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Invalid API key", status_code=401))
    client = TokenAPI(api_key="bad-key", user_agent="test-agent", env=test_env)

    req = CreateCrawlAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        format=Format.markdown,
    )
    with pytest.raises(Exception) as excinfo:
        client.get_crawl_token(req)

    assert isinstance(excinfo.value, UnauthorizedError)


def test_get_crawl_token_unauthorized_host(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Bad Request", status_code=400))

    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateCrawlAccessTokenRequest(
        url="https://nosuchurl.com",
        userAgent="test-agent",
        format=Format.markdown,
    )

    with pytest.raises(Exception) as excinfo:
        client.get_crawl_token(req)
    assert isinstance(excinfo.value, BadRequestError)


def test_get_crawl_token_server_error(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Server Error", status_code=500))

    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateCrawlAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        format=Format.markdown,
    )
    with pytest.raises(Exception) as excinfo:
        client.get_crawl_token(req)
    assert isinstance(excinfo.value, ServerError)


def test_get_crawl_token_unknown_error(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Teapots on the attack", status_code=418))

    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateCrawlAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        format=Format.markdown,
    )
    with pytest.raises(Exception) as excinfo:
        client.get_crawl_token(req)
    assert isinstance(excinfo.value, UnknownError)


def test_get_crawl_token_unreachable(mock_server_down, test_env):
    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateCrawlAccessTokenRequest(
        url="https://example.com",
        userAgent="test-agent",
        format=Format.markdown,
    )

    with pytest.raises(Exception) as excinfo:
        client.get_crawl_token(req)

    assert isinstance(excinfo.value, ServerError)
