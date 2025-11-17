import pytest
from tollbit.crawl_content.client import CrawlContentClient
from tollbit._apis.content_api import ContentAPI
from unittest.mock import MagicMock
from test_helpers.stub_api_responses import stub_catalog_response


@pytest.mark.parametrize(
    "url",
    [
        "example.com/bar",
        "https://example.com/bar",
    ],
)
def test_get_content_catalog(url):
    fake_catalog = [stub_catalog_response()]
    mock_content_api = MagicMock(spec=ContentAPI)
    mock_content_api.get_content_catalog.return_value = fake_catalog

    client = CrawlContentClient(content_api=mock_content_api, token_api=None)

    result = client.get_content_catalog(url)
    mock_content_api.get_content_catalog.assert_called_with(
        content_domain="example.com", page_size=100, page_token=None
    )
    assert result == fake_catalog[0]


def test_get_content_catalog_no_results():
    mock_content_api = MagicMock(spec=ContentAPI)
    mock_content_api.get_content_catalog.return_value = []

    client = CrawlContentClient(content_api=mock_content_api, token_api=None)

    result = client.get_content_catalog("https://nonexistent.com")
    assert result is None
