import httpx
import anyio
from typing import Any
from tollbit._environment import Environment
from tollbit._apis.models import (
    SelfReportContentUsageRequest,
    SelfReportContentUsageResponse,
)
from tollbit._apis.errors import (
    ApiError,
    ServerError,
)
from pydantic import BaseModel, TypeAdapter
from tollbit._logging import get_sdk_logger

_SELF_REPORTING_API_BASE_PATH = "/dev/v2/transactions/selfReport"

logger = get_sdk_logger(__name__)

T = TypeAdapter


class AsyncSelfReportingAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self.api_key = api_key
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    async def post_self_report(
        self, request: SelfReportContentUsageRequest
    ) -> SelfReportContentUsageResponse:
        logger.debug(
            "Reporting usages...",
            extra={
                "request": request.model_dump(),
                "url": f"{self._base_url}{_SELF_REPORTING_API_BASE_PATH}",
                "headers": self._headers(),
            },
        )
        try:
            response = await self._post_model(
                _SELF_REPORTING_API_BASE_PATH, self._headers(), request
            )
        except httpx.RequestError as e:
            logger.error(f"Connection error occurred: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        logger.debug(
            "Received self reporting response",
            extra={"status_code": response.status_code, "response_text": response.text},
        )
        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(str(err))
            raise err

        return TypeAdapter(SelfReportContentUsageResponse).validate_python(response.json())

    async def _post_model(
        self, path: str, headers: dict[str, str], body: BaseModel
    ) -> httpx.Response:
        payload = body.model_dump(mode="json", by_alias=True, exclude_none=True)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{self._base_url}{path}", headers=headers, json=payload
            )
        return response

    def _headers(self) -> dict[str, str]:
        return {
            "TollbitKey": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }


class SelfReportingAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self._env = env
        self._async_api = AsyncSelfReportingAPI(
            api_key=api_key,
            user_agent=user_agent,
            env=env,
        )

    def post_self_report(
        self, request: SelfReportContentUsageRequest
    ) -> SelfReportContentUsageResponse:
        return anyio.run(self._async_api.post_self_report, request, backend=self._env.anyio_backend)
