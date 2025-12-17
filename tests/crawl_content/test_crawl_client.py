import pytest
from tollbit.crawl_content.client import CrawlContentClient
from tollbit._apis.content_api import ContentAPI
from tollbit._apis.content_retrieval_api import ContentRetrievalAPI
from tollbit._apis.token_api import TokenAPI
from tollbit._apis.models import CreateCrawlAccessTokenRequest, CreateCrawlAccessTokenResponse
from tollbit.tokens import TollbitToken
from unittest.mock import MagicMock
from test_helpers.stub_api_responses import stub_catalog_response, stub_crawl_response
from tollbit.content_formats import Format


@pytest.mark.parametrize(
    "url",
    [
        "example.com/bar",
        "https://example.com/bar",
    ],
)
def test_get_content_catalog(url):
    fake_catalog = stub_catalog_response()
    mock_content_api = MagicMock(spec=ContentAPI)
    mock_content_api.get_content_catalog.return_value = fake_catalog

    client = CrawlContentClient(
        content_api=mock_content_api, token_api=None, content_retrieval_api=None
    )

    result = client.list_content_catalog(url)
    mock_content_api.get_content_catalog.assert_called_with(
        content_domain="example.com", page_size=100, page_token=None
    )
    assert result == fake_catalog


def test_crawl_content():
    fake_token_str = "tok_123"
    fake_content_url = "example.com/bar"
    fake_response = stub_crawl_response()

    mock_content_retrieval_api = MagicMock(spec=ContentRetrievalAPI)
    mock_content_retrieval_api.get_content.return_value = fake_response

    mock_token_api = MagicMock(spec=TokenAPI)
    mock_token_api.user_agent = "test-agent"
    mock_token_api.get_crawl_token.return_value = CreateCrawlAccessTokenResponse(
        token=fake_token_str,
    )
    # Call the method
    client = CrawlContentClient(
        content_api=None, token_api=mock_token_api, content_retrieval_api=mock_content_retrieval_api
    )
    result = client.crawl_content(
        url=fake_content_url,
    )

    # Assert
    mock_token_api.get_crawl_token.assert_called_once_with(
        CreateCrawlAccessTokenRequest(
            url="https://example.com/bar",
            userAgent="test-agent",
        )
    )

    mock_content_retrieval_api.get_content.assert_called_once_with(
        content_url=fake_content_url, token=TollbitToken(fake_token_str), format=Format.markdown
    )
    assert result == fake_response
