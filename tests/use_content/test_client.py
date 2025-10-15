import pytest
from tollbit.use_content.client import UseContentClient
from tollbit._apis.content_api import ContentAPI
from tollbit._apis.token_api import TokenAPI
from tollbit._apis.models import ContentRate
from unittest.mock import MagicMock
from test_helpers.stub_api_responses import stub_rate_response, stub_content_response
from tollbit.tokens import TollbitToken
from tollbit import currencies
from tollbit import licences
from tollbit._apis.models import (
    CreateSubdomainAccessTokenRequest,
    CreateSubdomainAccessTokenResponse,
)
from tollbit.content_formats import Format


@pytest.mark.parametrize(
    "url",
    [
        "example.com/bar",
        "https://example.com/bar",
    ],
)
def test_get_rate_calls_variants(url):
    fake_rate = [stub_rate_response()]
    mock_content_api = MagicMock(spec=ContentAPI)
    mock_content_api.get_rate.return_value = fake_rate

    mock_token_api = MagicMock(spec=TokenAPI)

    client = UseContentClient(content_api=mock_content_api, token_api=mock_token_api)

    result = client.get_rate(url)
    mock_content_api.get_rate.assert_called_with("example.com/bar")
    assert result == fake_rate


def test_get_sanctioned_content():
    fake_token_str = "tok_123"
    fake_content_url = "example.com/bar"
    fake_response = stub_content_response()

    mock_content_api = MagicMock(spec=ContentAPI)
    mock_content_api.get_content.return_value = [fake_response]

    mock_token_api = MagicMock(spec=TokenAPI)
    mock_token_api.user_agent = "test-agent"
    mock_token_api.get_token.return_value = CreateSubdomainAccessTokenResponse(
        token=fake_token_str,
        format="markdown",
    )
    # Call the method
    client = UseContentClient(content_api=mock_content_api, token_api=mock_token_api)
    result = client.get_sanctioned_content(
        url=fake_content_url,
        max_price_micros=1000000,
        currency=currencies.USD,
        license_type=licences.ON_DEMAND_LICENSE,
    )

    # Assert
    mock_token_api.get_token.assert_called_once_with(
        CreateSubdomainAccessTokenRequest(
            url="https://example.com/bar",
            userAgent="test-agent",
            maxPriceMicros=1000000,
            currency="USD",
            licenseType="ON_DEMAND_LICENSE",
            licenseCuid="",
            format="markdown",
        )
    )

    mock_content_api.get_content.assert_called_once_with(
        content_url=fake_content_url, token=TollbitToken(fake_token_str)
    )
    assert result == fake_response


def test_get_sanctioned_content_with_html():
    fake_token_str = "tok_123"
    fake_content_url = "example.com/bar"
    fake_response = stub_content_response()

    mock_content_api = MagicMock(spec=ContentAPI)
    mock_content_api.get_content.return_value = [fake_response]

    mock_token_api = MagicMock(spec=TokenAPI)
    mock_token_api.user_agent = "test-agent"
    mock_token_api.get_token.return_value = CreateSubdomainAccessTokenResponse(
        token=fake_token_str,
        format="markdown",
    )
    # Call the method
    client = UseContentClient(content_api=mock_content_api, token_api=mock_token_api)
    result = client.get_sanctioned_content(
        url=fake_content_url,
        max_price_micros=1000000,
        currency=currencies.USD,
        license_type=licences.ON_DEMAND_LICENSE,
        format=Format.html,
    )

    # Assert
    mock_token_api.get_token.assert_called_once_with(
        CreateSubdomainAccessTokenRequest(
            url="https://example.com/bar",
            userAgent="test-agent",
            maxPriceMicros=1000000,
            currency="USD",
            licenseType="ON_DEMAND_LICENSE",
            licenseCuid="",
            format="html",
        )
    )
    mock_content_api.get_content.assert_called_once_with(
        content_url=fake_content_url, token=TollbitToken(fake_token_str)
    )

    assert result == fake_response
