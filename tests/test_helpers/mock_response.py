from unittest.mock import Mock
import httpx
import respx
import requests
import pytest
import pprint
import difflib
import json


# --- Mocks and Fixtures ---


class MockResponse:
    def __init__(self, json_obj=None, problem_json_obj=None, body_text=None, status_code=200):
        self._json_obj = json_obj or []
        self._problem_json_obj = problem_json_obj or []
        self.body_text = body_text
        self.status_code = status_code

    def json(self):
        return self._json_obj or self._problem_json_obj

    @property
    def text(self):
        return self.body_text

    @property
    def headers(self):
        if self._problem_json_obj is not None:
            return {"Content-Type": "application/problem+json"}
        elif self._json_obj is not None:
            return {"Content-Type": "application/json"}
        else:
            return {"Content-Type": "text/plain"}

    @property
    def reason(self):
        return self.body_text or "OK"


# Patch requests.get for testing
@pytest.fixture()
def patch_requests_get(monkeypatch):
    def _patch_requests_get(response: MockResponse):
        mock_get = Mock(return_value=response)
        monkeypatch.setattr(requests, "get", mock_get)
        return mock_get

    return _patch_requests_get


@pytest.fixture()
def patch_requests_post(monkeypatch):
    def _patch_requests_post(response: MockResponse):
        post_mock = Mock(return_value=response)
        monkeypatch.setattr(requests, "post", post_mock)

        return post_mock

    return _patch_requests_post


@pytest.fixture()
def mock_server_down(monkeypatch):
    def _raise_connection_error(url, headers=None, json=None):
        raise requests.ConnectionError("Unable to connect to the server")

    monkeypatch.setattr(requests, "post", _raise_connection_error)


@pytest.fixture()
def mock_httpx_server_down(respx_mock):
    def _mock_httpx_server_down(url: str):
        respx_mock.post(url).mock(side_effect=httpx.RequestError("Unable to connect to the server"))
        respx_mock.get(url).mock(side_effect=httpx.RequestError("Unable to connect to the server"))

    return _mock_httpx_server_down


def assert_request_made(route: respx.Route) -> httpx.Request | None:
    if not route.called:
        raise AssertionError("Expected request to have been made, but it was not.")
    return route.calls[0].request


def assert_httpx_request_headers(request: httpx.Request, expected_headers: dict[str, str]):
    actual_headers = request.headers

    errors = []

    for key, expected_value in expected_headers.items():
        actual_value = actual_headers.get(key)
        if actual_value != expected_value:
            errors.append(
                f"Header '{key}' mismatch:\nExpected: {expected_value}\nActual:   {actual_value}"
            )

    if errors:
        raise AssertionError("\n".join(errors))


def assert_httpx_request_json_body(request: httpx.Request, expected_json: dict):
    raw_json = request.content
    request_body_json = json.loads(raw_json.decode("utf-8"))

    if request_body_json != expected_json:
        expected_str = pprint.pformat(expected_json)
        actual_str = pprint.pformat(request_body_json)
        diff = "\n".join(
            difflib.unified_diff(
                expected_str.splitlines(),
                actual_str.splitlines(),
                fromfile="expected",
                tofile="actual",
            )
        )
        raise AssertionError(f"JSON body mismatch:\n{diff}")


def assert_json_request_called_with(mock_post, expected_url, expected_headers, expected_json):
    assert mock_post.called, "Expected 'post' to have been called, but it was not."
    actual_call = mock_post.call_args
    actual_args, actual_kwargs = actual_call

    errors = []

    if actual_args[0] != expected_url:
        errors.append(f"URL mismatch:\nExpected: {expected_url}\nActual:   {actual_args[0]}")

    if actual_kwargs.get("headers") != expected_headers:
        errors.append(
            f"Headers mismatch:\nExpected: {expected_headers}\nActual:   {actual_kwargs.get('headers')}"
        )

    if actual_kwargs.get("json") != expected_json:
        expected_str = pprint.pformat(expected_json)
        actual_str = pprint.pformat(actual_kwargs.get("json"))
        diff = "\n".join(
            difflib.unified_diff(
                expected_str.splitlines(),
                actual_str.splitlines(),
                fromfile="expected",
                tofile="actual",
            )
        )
        errors.append(f"JSON body mismatch:\n{diff}")

    if errors:
        raise AssertionError("\n\n".join(errors))
