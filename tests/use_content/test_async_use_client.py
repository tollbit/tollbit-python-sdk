import pytest
from tollbit.use_content.client import AsyncUseContentClient
from tollbit._apis.token_api import AsyncTokenAPI
from tollbit._apis.content_retrieval_api import AsyncContentRetrievalAPI
from unittest.mock import AsyncMock, MagicMock
from tollbit.tokens import TollbitToken
from tollbit import currencies
from tollbit import licences
from tollbit._apis.models import (
    CreateSubdomainAccessTokenRequest,
    CreateSubdomainAccessTokenResponse,
)
from tollbit.content_formats import Format


@pytest.mark.anyio
async def test_get_sanctioned_content_async():
    fake_token_str = "tok_123"
    fake_content_url = "example.com/bar"
    fake_response = object()

    mock_content_retrieval_api = AsyncMock(spec=AsyncContentRetrievalAPI)
    mock_content_retrieval_api.get_content.return_value = fake_response

    mock_token_api = MagicMock(spec=AsyncTokenAPI)
    mock_token_api.user_agent = "test-agent"
    mock_token_api.get_content_token = AsyncMock(
        return_value=CreateSubdomainAccessTokenResponse(token=fake_token_str)
    )

    client = AsyncUseContentClient(
        token_api=mock_token_api, content_retrieval_api=mock_content_retrieval_api
    )
    result = await client.get_sanctioned_content(
        url=fake_content_url,
        max_price_micros=1000000,
        currency=currencies.USD,
        license_type=licences.types.ON_DEMAND_LICENSE,
    )

    mock_token_api.get_content_token.assert_awaited_once_with(
        CreateSubdomainAccessTokenRequest(
            url="https://example.com/bar",
            userAgent="test-agent",
            maxPriceMicros=1000000,
            currency="USD",
            licenseType="ON_DEMAND_LICENSE",
            licenseCuid="",
        )
    )
    mock_content_retrieval_api.get_content.assert_awaited_once_with(
        content_url=fake_content_url, token=TollbitToken(fake_token_str), format=Format.markdown
    )
    assert result == fake_response


@pytest.mark.anyio
async def test_get_sanctioned_content_with_html_async():
    fake_token_str = "tok_123"
    fake_content_url = "example.com/bar"
    fake_response = object()

    mock_content_retrieval_api = AsyncMock(spec=AsyncContentRetrievalAPI)
    mock_content_retrieval_api.get_content.return_value = fake_response

    mock_token_api = MagicMock(spec=AsyncTokenAPI)
    mock_token_api.user_agent = "test-agent"
    mock_token_api.get_content_token = AsyncMock(
        return_value=CreateSubdomainAccessTokenResponse(token=fake_token_str, format="markdown")
    )

    client = AsyncUseContentClient(
        token_api=mock_token_api, content_retrieval_api=mock_content_retrieval_api
    )
    result = await client.get_sanctioned_content(
        url=fake_content_url,
        max_price_micros=1000000,
        currency=currencies.USD,
        license_type=licences.types.ON_DEMAND_LICENSE,
        format=Format.html,
    )

    mock_token_api.get_content_token.assert_awaited_once_with(
        CreateSubdomainAccessTokenRequest(
            url="https://example.com/bar",
            userAgent="test-agent",
            maxPriceMicros=1000000,
            currency="USD",
            licenseType="ON_DEMAND_LICENSE",
            licenseCuid="",
        )
    )
    mock_content_retrieval_api.get_content.assert_awaited_once_with(
        content_url=fake_content_url, token=TollbitToken(fake_token_str), format=Format.html
    )
    assert result == fake_response
