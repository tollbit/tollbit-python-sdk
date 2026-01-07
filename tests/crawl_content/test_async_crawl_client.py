import pytest
from tollbit.crawl_content.client import AsyncCrawlContentClient
from tollbit._apis.content_api import AsyncContentAPI
from tollbit._apis.content_retrieval_api import AsyncContentRetrievalAPI
from tollbit._apis.token_api import AsyncTokenAPI
from tollbit._apis.models import CreateCrawlAccessTokenRequest, CreateCrawlAccessTokenResponse
from tollbit.tokens import TollbitToken
from unittest.mock import AsyncMock, MagicMock
from test_helpers.stub_api_responses import stub_catalog_response, stub_crawl_response
from tollbit.content_formats import Format


@pytest.mark.anyio
async def test_list_content_catalog_async():
    fake_catalog = stub_catalog_response()
    mock_content_api = AsyncMock(spec=AsyncContentAPI)
    mock_content_api.get_content_catalog.return_value = fake_catalog

    client = AsyncCrawlContentClient(
        token_api=None, content_retrieval_api=None, content_api=mock_content_api
    )

    result = await client.list_content_catalog("example.com/bar")
    mock_content_api.get_content_catalog.assert_awaited_with(
        content_domain="example.com", page_size=100, page_token=None
    )
    assert result == fake_catalog


@pytest.mark.anyio
async def test_crawl_content_async():
    fake_token_str = "tok_123"
    fake_content_url = "example.com/bar"
    fake_response = stub_crawl_response()

    mock_content_retrieval_api = AsyncMock(spec=AsyncContentRetrievalAPI)
    mock_content_retrieval_api.get_content.return_value = fake_response

    mock_token_api = MagicMock(spec=AsyncTokenAPI)
    mock_token_api.user_agent = "test-agent"
    mock_token_api.get_crawl_token = AsyncMock(
        return_value=CreateCrawlAccessTokenResponse(token=fake_token_str)
    )

    client = AsyncCrawlContentClient(
        token_api=mock_token_api, content_retrieval_api=mock_content_retrieval_api, content_api=None
    )
    result = await client.crawl_content(
        url=fake_content_url,
    )

    mock_token_api.get_crawl_token.assert_awaited_once_with(
        CreateCrawlAccessTokenRequest(
            url="https://example.com/bar",
            userAgent="test-agent",
        )
    )
    mock_content_retrieval_api.get_content.assert_awaited_once_with(
        content_url=fake_content_url, token=TollbitToken(fake_token_str), format=Format.markdown
    )
    assert result == fake_response
