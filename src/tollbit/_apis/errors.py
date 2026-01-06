from __future__ import annotations
from tollbit._apis.models import ProblemJSON
from tollbit._logging import get_sdk_logger
from httpx import Response

logger = get_sdk_logger(__name__)


class ApiError(RuntimeError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        status_code: int,
        raw_message: str | None = None,
        problem_json: ProblemJSON | None = None,
    ):
        super().__init__("")
        self.status_code = status_code
        self._problem_json = problem_json
        self._raw_message = raw_message

    @classmethod
    def from_response(cls, response: Response) -> ApiError:
        content_type = response.headers.get("Content-Type", "")
        if "application/problem+json" in content_type:
            try:
                problem_json = ProblemJSON.model_validate(response.json())
                return cls(
                    status_code=response.status_code,
                    problem_json=problem_json,
                )
            except Exception as e:
                logger.warning(
                    f"Failed to parse application/json response as ProblemJSON from response: {e}"
                )
                return cls(
                    status_code=response.status_code,
                    raw_message=response.reason_phrase,
                )

        return cls(status_code=response.status_code, raw_message=response.text)

    def __str__(self) -> str:
        if self._problem_json:
            return f"API Error: ({self.status_code}) {self.title} - {self.detail} (instance: {self.instance})"
        if self._raw_message:
            return f"API Error: ({self.status_code}) {self._raw_message}"

        return "API Error: Unknown Error"

    @property
    def detail(self) -> str | None:
        if self._problem_json:
            return self._problem_json.detail
        return None

    @property
    def instance(self) -> str | None:
        if self._problem_json:
            return self._problem_json.instance
        return None

    @property
    def title(self) -> str:
        if self._problem_json:
            return self._problem_json.title

        return self._raw_message or "Unknown Error"


class UnauthorizedError(RuntimeError):
    pass


class BadRequestError(RuntimeError):
    pass


class ServerError(RuntimeError):
    pass


class ParseResponseError(RuntimeError):
    """Raised when there is an error parsing the response from the API."""

    pass


class UnknownError(RuntimeError):
    pass
