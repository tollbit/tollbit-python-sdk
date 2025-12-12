import requests
from tollbit._environment import Environment
from tollbit._apis.models import (
    DeveloperSelfReportRequest,
    DeveloperTransactionResponse,
)
from tollbit._apis.errors import (
    UnauthorizedError,
    BadRequestError,
    ServerError,
    UnknownError,
)
from pydantic import TypeAdapter
from tollbit._logging import get_sdk_logger

_SELF_REPORTING_API_BASE_PATH = "/dev/v1/transactions/selfReport"

logger = get_sdk_logger(__name__)


class SelfReportingAPI:
    api_key: str
    user_agent: str
    _base_url: str

    def __init__(
        self,
        api_key: str,
        user_agent: str,
        env: Environment,
    ):
        self.api_key = api_key
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    def post_self_report(
        self, request: DeveloperSelfReportRequest
    ) -> list[DeveloperTransactionResponse]:
        try:
            headers = {"User-Agent": self.user_agent, "TollbitKey": self.api_key}
            url = f"{self._base_url}{_SELF_REPORTING_API_BASE_PATH}"
            json_body = request.model_dump(mode="json", by_alias=True)
            logger.debug(
                "reporting usages...",
                extra={"request": json_body, "url": url, "headers": headers},
            )
            response = requests.post(
                url,
                headers=headers,
                json=json_body,
            )
        except requests.RequestException as e:
            raise ServerError("Unable to connect to the Tollbit server") from e

        match response.status_code:
            case 200:
                logger.debug("Raw response", extra={"response_text": response.text})
                resp: list[DeveloperTransactionResponse] = TypeAdapter(
                    list[DeveloperTransactionResponse]
                ).validate_python(response.json())
                return resp
            case 400:
                raise BadRequestError("Bad request sent to the Tollbit server")
            case 401:
                raise UnauthorizedError("Unauthorized: Invalid API key")
            case 500:
                raise ServerError("Internal server error at Tollbit")
            case _:
                raise UnknownError(f"Unexpected status code: {response.status_code}")
