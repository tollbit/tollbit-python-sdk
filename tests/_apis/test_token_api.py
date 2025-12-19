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
from test_helpers.mock_response import (
    MockResponse,
    patch_requests_post,
    mock_server_down,
    assert_json_request_called_with,
)


# --- Tests for Content Access Token ---
def test_get_content_token_success(patch_requests_post, test_env):
    post_mock = patch_requests_post(MockResponse(json_obj={"token": "TOKEN-ABC123"}))
    client = TokenAPI(api_key="test-key", user_agent="test-agent", env=test_env)
    req = CreateSubdomainAccessTokenRequest(
        url="https://example.com",
        user_agent="test-agent",
        max_price_micros=1000000,
        currency="USD",
        license_type="ON_DEMAND_LICENSE",
        license_cuid="",
    )
    response = client.get_content_token(req)
    assert response.token == "TOKEN-ABC123"
    assert_json_request_called_with(
        post_mock,
        expected_url=f"{test_env.developer_api_base_url}/dev/v2/tokens/content",
        expected_headers={
            "User-Agent": "test-agent",
            "TollbitKey": "test-key",
            "Content-Type": "application/json",
        },
        expected_json={
            "url": "https://example.com/",
            "userAgent": "test-agent",
            "maxPriceMicros": 1000000,
            "currency": "USD",
            "licenseType": "ON_DEMAND_LICENSE",
            "licenseCuid": "",
        },
    )


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
