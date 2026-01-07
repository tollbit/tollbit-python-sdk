import requests
import httpx
from pydantic import BaseModel, TypeAdapter
from typing import Type, TypeVar, Any
from tollbit._environment import Environment
from tollbit._apis.models import (
    CreateSubdomainAccessTokenRequest,
    CreateSubdomainAccessTokenResponse,
    CreateCrawlAccessTokenRequest,
    CreateCrawlAccessTokenResponse,
)
from tollbit._apis.errors import (
    UnauthorizedError,
    BadRequestError,
    ServerError,
    UnknownError,
    ApiError,
)
from tollbit._environment import Environment
from tollbit._logging import get_sdk_logger
import anyio

CREATE_CONTENT_TOKEN_PATH = "/dev/v2/tokens/content"
CREATE_CRAWL_TOKEN_PATH = "/dev/v2/tokens/crawl"

# Configure logging
logger = get_sdk_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class AsyncTokenAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self.api_key = api_key
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    async def get_content_token(
        self, req: CreateSubdomainAccessTokenRequest
    ) -> CreateSubdomainAccessTokenResponse:
        logger.debug(
            "Requesting subdomain access token...",
            extra={
                "request": req.model_dump(),
                "url": f"{self._base_url}{CREATE_CONTENT_TOKEN_PATH}",
                "headers": self._headers(),
            },
        )
        try:
            response = await self._post_model(CREATE_CONTENT_TOKEN_PATH, self._headers(), req)
        except httpx.RequestError as e:
            logger.error(f"Connection error occurred: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        return _handle_response(response, CreateSubdomainAccessTokenResponse)

    async def get_crawl_token(
        self, req: CreateCrawlAccessTokenRequest
    ) -> CreateCrawlAccessTokenResponse:
        logger.debug(
            "Requesting crawl access token...",
            extra={
                "request": req.model_dump(),
                "url": f"{self._base_url}{CREATE_CRAWL_TOKEN_PATH}",
                "headers": self._headers(),
            },
        )
        try:
            response = await self._post_model(CREATE_CRAWL_TOKEN_PATH, self._headers(), req)
        except httpx.RequestError as e:
            logger.error(f"Connection error occurred: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        return _handle_response(response, CreateCrawlAccessTokenResponse)

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


class TokenAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self._env = env
        self.user_agent = user_agent
        self._async_token_api = AsyncTokenAPI(
            api_key=api_key,
            user_agent=user_agent,
            env=env,
        )

    def get_content_token(
        self, req: CreateSubdomainAccessTokenRequest
    ) -> CreateSubdomainAccessTokenResponse:
        return anyio.run(
            self._async_token_api.get_content_token, req, backend=self._env.anyio_backend
        )

    def get_crawl_token(self, req: CreateCrawlAccessTokenRequest) -> CreateCrawlAccessTokenResponse:
        return anyio.run(
            self._async_token_api.get_crawl_token, req, backend=self._env.anyio_backend
        )


def _handle_response(response: httpx.Response, success_model: Type[T]) -> T:
    if response.status_code != 200:
        err = ApiError.from_response(response)
        logger.error(str(err))
        raise err

    result: T = TypeAdapter(success_model).validate_python(response.json())
    return result
