import pytest
from tollbit._apis.errors import ApiError
from tollbit._apis.models import ProblemJSON
from httpx import Response


def test_api_error_parse_with_problem_json():
    response = Response(
        400,
        json={
            "status": 400,
            "type": "about:blank",
            "title": "Bad Request",
            "detail": "You forgot to do the thing",
            "instance": "/path/to/resource",
        },
        headers={"Content-Type": "application/problem+json"},
    )

    error = ApiError.from_response(response)
    assert error.status_code == 400
    assert error.detail == "You forgot to do the thing"
    assert error.instance == "/path/to/resource"
    assert error.title == "Bad Request"
    assert (
        str(error)
        == "API Error: (400) Bad Request - You forgot to do the thing (instance: /path/to/resource)"
    )


def test_api_error_str_without_problem_json():
    response = Response(500, text="Internal Server Error")

    error = ApiError.from_response(response)
    assert error.status_code == 500
    assert error.title == "Internal Server Error"
    assert error.detail is None
    assert error.instance is None
    assert str(error) == "API Error: (500) Internal Server Error"
