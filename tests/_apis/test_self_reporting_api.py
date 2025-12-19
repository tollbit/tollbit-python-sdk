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
from test_helpers.mock_response import (
    MockResponse,
    patch_requests_post,
    mock_server_down,
    assert_json_request_called_with,
)


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
    post_mock = patch_requests_post(MockResponse(json_obj=fake_transaction_response))
    client = SelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)

    req = SelfReportContentUsageRequest(
        idempotency_id="unique-id-123",
        usage=[
            SelfReportUsage(
                url="https://example.com/path/to/content",
                times_used=3,
                license_permissions=[{"name": "PARTIAL_USE"}],
                license_id="license-cuid-123",
                license_type="standard",
            )
        ],
    )

    resp = client.post_self_report(req)

    assert_json_request_called_with(
        post_mock,
        expected_url=f"{test_env.developer_api_base_url}/dev/v2/transactions/selfReport",
        expected_headers={"TollbitKey": "test-secret-key", "User-Agent": "test-agent"},
        expected_json={
            "idempotencyId": "unique-id-123",
            "usage": [
                {
                    "url": "https://example.com/path/to/content",
                    "timesUsed": 3,
                    "licensePermissions": [{"name": "PARTIAL_USE"}],
                    "licenseId": "license-cuid-123",
                    "licenseType": "standard",
                }
            ],
        },
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
