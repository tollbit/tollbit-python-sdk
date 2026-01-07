from __future__ import annotations
import httpx
import anyio
from pydantic import TypeAdapter
from tollbit._environment import Environment
from tollbit._apis.models._generated.openapi_tollbit_apis import PagedSearchResultResponse
from tollbit._apis.errors import (
    ServerError,
    ApiError,
)
from tollbit._logging import get_sdk_logger

_SEARCH_PATH = "/dev/v2/search"

logger = get_sdk_logger(__name__)


class AsyncSearchAPI:
    api_key: str
    user_agent: str
    _base_url: str

    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self.api_key = api_key
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    async def search(
        self,
        q: str,
        size: int | None = None,
        next_token: str | None = None,
        properties: str | None = None,
    ) -> PagedSearchResultResponse:
        headers = self._headers()
        url = f"{self._base_url}{_SEARCH_PATH}"
        params: dict[str, str | int] = {"q": q}
        if size is not None:
            params["size"] = size
        if next_token is not None:
            params["next-token"] = next_token
        if properties is not None:
            params["properties"] = properties

        logger.debug(
            "Requesting search results...",
            extra={"url": url, "headers": headers, "params": params},
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
        except httpx.RequestError as e:
            logger.error(f"Error occurred while searching: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        logger.debug(
            "Received search response",
            extra={"status_code": response.status_code, "response_text": response.text},
        )

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(str(err))
            raise err

        resp: PagedSearchResultResponse = TypeAdapter(PagedSearchResultResponse).validate_python(
            response.json()
        )
        return resp

    def _headers(self) -> dict[str, str]:
        return {
            "TollbitKey": self.api_key,
            "User-Agent": self.user_agent,
        }


class SearchAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self._env = env
        self._async_api = AsyncSearchAPI(api_key=api_key, user_agent=user_agent, env=env)

    def search(
        self,
        q: str,
        size: int | None = None,
        next_token: str | None = None,
        properties: str | None = None,
    ) -> PagedSearchResultResponse:
        return anyio.run(
            self._async_api.search,
            q,
            size,
            next_token,
            properties,
            backend=self._env.anyio_backend,
        )
