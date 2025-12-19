import requests
from tollbit._environment import Environment
from tollbit._apis.models import (
    SelfReportContentUsageRequest,
    SelfReportContentUsageResponse,
)
from tollbit._apis.errors import (
    ApiError,
    ServerError,
)
from pydantic import TypeAdapter
from tollbit._logging import get_sdk_logger

_SELF_REPORTING_API_BASE_PATH = "/dev/v2/transactions/selfReport"

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
        self, request: SelfReportContentUsageRequest
    ) -> SelfReportContentUsageResponse:
        try:
            headers = {"User-Agent": self.user_agent, "TollbitKey": self.api_key}
            url = f"{self._base_url}{_SELF_REPORTING_API_BASE_PATH}"
            json_body = request.model_dump(mode="json", by_alias=True, exclude_none=True)
            logger.debug(
                "reporting usages...",
                extra={"request": json_body, "url": url, "headers": headers},
            )
            response = requests.post(
                url,
                headers=headers,
                json=json_body,
            )

            logger.debug(
                "Received self reporting response",
                extra={"status_code": response.status_code, "response_text": response.text},
            )

        except requests.RequestException as e:
            raise ServerError("Unable to connect to the Tollbit server") from e

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(str(err))
            raise err

        resp: SelfReportContentUsageResponse = TypeAdapter(
            SelfReportContentUsageResponse
        ).validate_python(response.json())
        return resp
