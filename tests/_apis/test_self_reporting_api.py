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
    DeveloperSelfReportRequest,
    SelfReportUsage,
    DeveloperTransactionResponse,
)
import requests
from unittest import mock


# --- Mocks and Fixtures ---
class MockResponse:
    def __init__(self, json_obj=None, body_text=None, status_code=200):
        self._json_obj = json_obj or []
        self.body_text = body_text
        self.status_code = status_code

    def json(self):
        return self._json_obj

    @property
    def text(self):
        return self.body_text

    @property
    def headers(self):
        text_type = "application/json" if self._json_obj is not None else "text/plain"
        return {"Content-Type": text_type}

    @property
    def reason(self):
        return self.body_text or "OK"


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
        "url": "https://example.com/path/to/content",
        "perUnitPriceMicros": 5000,
        "totalUsePriceMicros": 15000,
        "currency": "USD",
        "license": {
            "cuid": "license-cuid-123",
            "licenseType": "standard",
            "licensePath": "/licenses/standard",
            "permissions": [{"name": "PARTIAL_USE"}],
        },
    }
    patch_requests_post(MockResponse(json_obj=[fake_transaction_response]))
    client = SelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)

    req = DeveloperSelfReportRequest(
        idempotency_id="unique-id-123",
        usage=[
            SelfReportUsage(
                url="https://example.com/path/to/content",
                times_used=3,
                license_permissions=[{"name": "PARTIAL_USE"}],
                license_cuid="license-cuid-123",
                license_type="standard",
            )
        ],
    )

    resp = client.post_self_report(req)

    requests.post.assert_called_with(
        f"{test_env.developer_api_base_url}/dev/v1/transactions/selfReport",
        headers={"TollbitKey": "test-secret-key", "User-Agent": "test-agent"},
        json=req.model_dump(mode="json", by_alias=True),
    )

    assert isinstance(resp, list)
    assert isinstance(resp[0], DeveloperTransactionResponse)


def test_report_bad_request(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Bad Request", status_code=400))
    client = SelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    req = DeveloperSelfReportRequest(
        idempotency_id="unique-id-123",
        usage=[
            SelfReportUsage(
                url="https://example.com/path/to/content",
                times_used=3,
                license_permissions=[{"name": "PARTIAL_USE"}],
                license_cuid="license-cuid-123",
                license_type="standard",
            )
        ],
    )

    with pytest.raises(BadRequestError):
        client.post_self_report(req)


def test_report_server_error(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Server Error", status_code=500))
    client = SelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    req = DeveloperSelfReportRequest(
        idempotency_id="unique-id-123",
        usage=[
            SelfReportUsage(
                url="https://example.com/path/to/content",
                times_used=3,
                license_permissions=[{"name": "PARTIAL_USE"}],
                license_cuid="license-cuid-123",
                license_type="standard",
            )
        ],
    )

    with pytest.raises(ServerError):
        client.post_self_report(req)


def test_report_unknown_error(patch_requests_post, test_env):
    patch_requests_post(MockResponse(body_text="Teapots on the attack", status_code=418))
    client = SelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    req = DeveloperSelfReportRequest(
        idempotency_id="unique-id-123",
        usage=[
            SelfReportUsage(
                url="https://example.com/path/to/content",
                times_used=3,
                license_permissions=[{"name": "PARTIAL_USE"}],
                license_cuid="license-cuid-123",
                license_type="standard",
            )
        ],
    )

    with pytest.raises(UnknownError):
        client.post_self_report(req)


def test_report_unreachable(mock_server_down, test_env):
    client = SelfReportingAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)
    req = DeveloperSelfReportRequest(
        idempotency_id="unique-id-123",
        usage=[
            SelfReportUsage(
                url="https://example.com/path/to/content",
                times_used=3,
                license_permissions=[{"name": "PARTIAL_USE"}],
                license_cuid="license-cuid-123",
                license_type="standard",
            )
        ],
    )

    with pytest.raises(ServerError):
        client.post_self_report(req)
