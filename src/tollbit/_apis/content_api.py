import httpx
import anyio
from pydantic import TypeAdapter
from tollbit._environment import Environment
from tollbit._apis.models import (
    DeveloperRateResponse,
    CatalogResponse,
)
from tollbit._apis.errors import (
    ApiError,
    ServerError,
)
from tollbit._logging import get_sdk_logger

_GET_RATE_PATH = "/dev/v2/rate/<PATH>"
_GET_CATALOG_PATH = "/dev/v2/content/<DOMAIN>/catalog/list"

# Configure logging
logger = get_sdk_logger(__name__)


class AsyncContentAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self.api_key = api_key
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    async def get_rate(self, content: str) -> list[DeveloperRateResponse]:
        headers = self._headers()
        url = f"{self._base_url}{_GET_RATE_PATH.replace('<PATH>', content)}"
        logger.debug(
            "Requesting content rate...",
            extra={"content": content, "url": url, "headers": headers},
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
        except httpx.RequestError as e:
            logger.error(f"Error occurred while fetching rate: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        logger.debug("Raw response", extra={"response_text": response.text})

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(str(err))
            raise err

        resp: list[DeveloperRateResponse] = TypeAdapter(
            list[DeveloperRateResponse]
        ).validate_python(response.json())
        return resp

    async def get_content_catalog(
        self,
        content_domain: str,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> CatalogResponse:
        headers = self._headers()
        url = f"{self._base_url}{_GET_CATALOG_PATH.replace('<DOMAIN>', content_domain)}"
        params: dict[str, str | int] = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token

        logger.debug(
            "Requesting content catalog...",
            extra={"url": url, "headers": headers, "params": params},
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
        except httpx.RequestError as e:
            logger.error(f"Error occurred while fetching content catalog: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        logger.debug(
            "Received content catalog response",
            extra={"status_code": response.status_code, "response_text": response.text},
        )

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(str(err))
            raise err

        resp: CatalogResponse = TypeAdapter(CatalogResponse).validate_python(response.json())
        return resp

    def _headers(self) -> dict[str, str]:
        return {
            "TollbitKey": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }


class ContentAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self._env = env
        self._async_api = AsyncContentAPI(api_key=api_key, user_agent=user_agent, env=env)

    def get_rate(self, content: str) -> list[DeveloperRateResponse]:
        return anyio.run(self._async_api.get_rate, content, backend=self._env.anyio_backend)

    def get_content_catalog(
        self,
        content_domain: str,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> CatalogResponse:
        return anyio.run(
            self._async_api.get_content_catalog,
            content_domain,
            page_size,
            page_token,
            backend=self._env.anyio_backend,
        )
