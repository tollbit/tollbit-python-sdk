import pytest
import httpx
from tollbit._apis.content_retrieval_api import AsyncContentRetrievalAPI
from tollbit._apis.errors import (
    BadRequestError,
    ServerError,
    ApiError,
)
from tollbit.tokens import TollbitToken
from tollbit._apis.models import GetContentResponse
from unittest import mock
from tollbit import content_formats
from test_helpers.mock_response import (
    assert_request_made,
    assert_httpx_request_headers,
    mock_httpx_server_down,
)


# --- Tests ---
# ======= Get Content Tests =======
@pytest.mark.anyio
async def test_get_content_success(respx_mock, test_env):
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
    get_content = respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/path/to/content"
    ).mock(return_value=httpx.Response(200, json=fake_content))

    client = AsyncContentRetrievalAPI(user_agent="test-agent", env=test_env)
    resp = await client.get_content(
        TollbitToken("dummy-token"), "example.com/path/to/content", content_formats.HTML
    )

    assert isinstance(resp, GetContentResponse)
    req = assert_request_made(get_content)
    assert_httpx_request_headers(
        req,
        {
            "User-Agent": "test-agent",
            "Tollbit-Token": "dummy-token",
            "Tollbit-Accept-Content": "text/html",
        },
    )


# https://linear.app/tollbit/issue/TOL-1184/getcontent-v2-returns-empty-response-for-no-content
@pytest.mark.skip(
    reason="This currently returns an empty object instead of a 404. We need to discuss this for V2"
)
@pytest.mark.anyio
async def test_get_content_no_content(respx_mock, test_env):
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

    respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/path/to/content"
    ).mock(return_value=httpx.Response(200, json=fake_response))

    client = AsyncContentRetrievalAPI(user_agent="test-agent", env=test_env)

    with pytest.raises(BadRequestError):
        await client.get_content(
            TollbitToken("dummy-token"), "nosuchurl.com/imaginary", content_formats.HTML
        )


@pytest.mark.anyio
async def test_get_content_problem_json_error(respx_mock, test_env):
    fake_response = {
        "detail": "Fail",
        "instance": "/dev/v2/content/pioneervalleygazette.com/daydream",
        "status": 500,
        "title": "Internal Server Error",
        "type": "about:blank",
    }

    respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/path/to/content"
    ).mock(
        return_value=httpx.Response(
            500, json=fake_response, headers={"Content-Type": "application/problem+json"}
        )
    )

    client = AsyncContentRetrievalAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        await client.get_content(
            TollbitToken("dummy-token"), "example.com/path/to/content", content_formats.HTML
        )

    error = exc_info.value
    assert (
        str(error)
        == "API Error: (500) Internal Server Error - Fail (instance: /dev/v2/content/pioneervalleygazette.com/daydream)"
    )


@pytest.mark.anyio
async def test_get_content_non_problem_json_error(respx_mock, test_env):
    respx_mock.get(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/path/to/content"
    ).mock(return_value=httpx.Response(418, text="Teapots on the attack"))
    client = AsyncContentRetrievalAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(ApiError) as exc_info:
        await client.get_content(
            TollbitToken("dummy-token"), "example.com/path/to/content", content_formats.HTML
        )

    error = exc_info.value
    assert str(error) == "API Error: (418) Teapots on the attack"


@pytest.mark.anyio
async def test_get_content_unreachable(mock_httpx_server_down, test_env):
    mock_httpx_server_down(
        f"{test_env.developer_api_base_url}/dev/v2/content/example.com/path/to/content"
    )

    client = AsyncContentRetrievalAPI(user_agent="test-agent", env=test_env)
    with pytest.raises(ServerError):
        await client.get_content(
            TollbitToken("dummy-token"), "example.com/path/to/content", content_formats.HTML
        )
