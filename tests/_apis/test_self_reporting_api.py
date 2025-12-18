import pytest
from tollbit._apis.self_reporting_api import SelfReportingAPI
from tollbit._apis.errors import (
    UnauthorizedError,
    BadRequestError,
    ServerError,
    UnknownError,
    ApiError,
)
from tollbit._apis.models import (
    SelfReportContentUsageRequest,
    SelfReportUsage,
    SelfReportContentUsageResponse,
)
import requests
from unittest import mock
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
def patch_requests_post(monkeypatch):
    def _patch_requests_post(response: MockResponse):
        mock_post = mock.Mock(return_value=response)
        monkeypatch.setattr(requests, "post", mock_post)
        return mock_post

    return _patch_requests_post


@pytest.fixture()
def mock_server_down(monkeypatch):
    def _raise_connection_error(url, headers=None, json=None):
        raise requests.ConnectionError("Unable to connect to the server")

    monkeypatch.setattr(requests, "get", _raise_connection_error)
    monkeypatch.setattr(requests, "post", _raise_connection_error)


# --- Tests ---
# ======= Get Rate Tests =======
def test_report_success(patch_requests_post, test_env):
    # Simulate a valid ContentRate list response
    fake_transaction_response = {
        "receipts": [
            {
                "url": "https://example.com/path/to/content",
                "perUnitPriceMicros": 5000,
                "totalUsePriceMicros": 15000,
                "currency": "USD",
                "license": {
                    "id": "license-cuid-123",
                    "licenseType": "standard",
                    "licensePath": "/licenses/standard",
                    "permissions": [{"name": "PARTIAL_USE"}],
                },
            }
        ]
    }
    patch_requests_post(MockResponse(json_obj=fake_transaction_response))
    client = SelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)

    req = SelfReportContentUsageRequest(
        idempotencyId="unique-id-123",
        usage=[
            SelfReportUsage(
                url="https://example.com/path/to/content",
                timesUsed=3,
                licensePermissions=[{"name": "PARTIAL_USE"}],
                licenseId="license-cuid-123",
                licenseType="standard",
            )
        ],
    )

    resp = client.post_self_report(req)

    requests.post.assert_called_with(
        f"{test_env.developer_api_base_url}/dev/v2/transactions/selfReport",
        headers={"TollbitKey": "test-secret-key", "User-Agent": "test-agent"},
        json=req.model_dump(mode="json", by_alias=True),
    )

    assert isinstance(resp, SelfReportContentUsageResponse)


def test_report_problem_json_error(patch_requests_post, test_env):
    fake_response = {
        "detail": "Fail",
        "instance": "/dev/v2/transactions/selfReport",
        "status": 500,
        "title": "Internal Server Error",
        "type": "about:blank",
    }

    patch_requests_post(MockResponse(problem_json_obj=fake_response, status_code=500))

    client = SelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    req = SelfReportContentUsageRequest(
        idempotencyId="unique-id-123",
        usage=[
            SelfReportUsage(
                url="https://example.com/path/to/content",
                timesUsed=3,
                licensePermissions=[{"name": "PARTIAL_USE"}],
                licenseId="license-cuid-123",
                licenseType="standard",
            )
        ],
    )
    with pytest.raises(ApiError) as exc_info:
        client.post_self_report(req)

    error = exc_info.value
    assert (
        str(error)
        == "API Error: (500) Internal Server Error - Fail (instance: /dev/v2/transactions/selfReport)"
    )


def test_report_non_problem_json_error(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Teapots on the attack", status_code=418))

    client = SelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    req = SelfReportContentUsageRequest(
        idempotencyId="unique-id-123",
        usage=[
            SelfReportUsage(
                url="https://example.com/path/to/content",
                timesUsed=3,
                licensePermissions=[{"name": "PARTIAL_USE"}],
                licenseId="license-cuid-123",
                licenseType="standard",
            )
        ],
    )
    with pytest.raises(ApiError) as exc_info:
        client.post_self_report(req)

    error = exc_info.value
    assert str(error) == "API Error: (418) Teapots on the attack"


def test_report_unreachable(mock_server_down, test_env):
    client = SelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    req = SelfReportContentUsageRequest(
        idempotencyId="unique-id-123",
        usage=[
            SelfReportUsage(
                url="https://example.com/path/to/content",
                timesUsed=3,
                licensePermissions=[{"name": "PARTIAL_USE"}],
                licenseId="license-cuid-123",
                licenseType="standard",
            )
        ],
    )
    with pytest.raises(ServerError):
        client.post_self_report(req)
