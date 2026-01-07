import pytest
import httpx
from tollbit._apis.self_reporting_api import AsyncSelfReportingAPI
from tollbit._apis.errors import (
    ServerError,
    ApiError,
)
from tollbit._apis.models import (
    SelfReportContentUsageRequest,
    SelfReportUsage,
    SelfReportContentUsageResponse,
)
from unittest import mock
from test_helpers.mock_response import (
    assert_request_made,
    assert_httpx_request_headers,
    assert_httpx_request_json_body,
    mock_httpx_server_down,
)


# ======= Self Reporting API Tests =======


@pytest.mark.anyio
async def test_report_success(respx_mock, test_env):
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
    route = respx_mock.post(
        f"{test_env.developer_api_base_url}/dev/v2/transactions/selfReport"
    ).mock(return_value=httpx.Response(200, json=fake_transaction_response))

    client = AsyncSelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
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
    resp = await client.post_self_report(req)
    assert isinstance(resp, SelfReportContentUsageResponse)
    req_obj = assert_request_made(route)
    assert_httpx_request_headers(
        req_obj,
        {
            "TollbitKey": "test-secret-key",
            "User-Agent": "test-agent",
            "Content-Type": "application/json",
        },
    )
    assert_httpx_request_json_body(
        req_obj,
        {
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


@pytest.mark.anyio
async def test_report_problem_json_error(respx_mock, test_env):
    fake_response = {
        "detail": "Fail",
        "instance": "/dev/v2/transactions/selfReport",
        "status": 500,
        "title": "Internal Server Error",
        "type": "about:blank",
    }
    respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/transactions/selfReport").mock(
        return_value=httpx.Response(
            500, json=fake_response, headers={"Content-Type": "application/problem+json"}
        )
    )

    client = AsyncSelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
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
    with pytest.raises(ApiError) as exc_info:
        await client.post_self_report(req)
    error = exc_info.value
    assert (
        str(error)
        == "API Error: (500) Internal Server Error - Fail (instance: /dev/v2/transactions/selfReport)"
    )


@pytest.mark.anyio
async def test_report_non_problem_json_error(respx_mock, test_env):
    respx_mock.post(f"{test_env.developer_api_base_url}/dev/v2/transactions/selfReport").mock(
        return_value=httpx.Response(418, text="Teapots on the attack")
    )

    client = AsyncSelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
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
    with pytest.raises(ApiError) as exc_info:
        await client.post_self_report(req)
    error = exc_info.value
    assert str(error) == "API Error: (418) Teapots on the attack"


@pytest.mark.anyio
async def test_report_unreachable(mock_httpx_server_down, test_env):
    mock_httpx_server_down(f"{test_env.developer_api_base_url}/dev/v2/transactions/selfReport")
    client = AsyncSelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
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
    with pytest.raises(ServerError):
        await client.post_self_report(req)
