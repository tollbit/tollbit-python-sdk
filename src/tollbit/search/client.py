from __future__ import annotations

from tollbit._apis.search_api import SearchAPI, AsyncSearchAPI
from tollbit._apis.models._generated.openapi_tollbit_apis import PagedSearchResultResponse
from tollbit._environment import env_from_vars
from tollbit._logging import get_sdk_logger

logger = get_sdk_logger(__name__)


def create_client(
    secret_key: str,
    user_agent: str,
) -> SearchClient:
    env = env_from_vars()

    return SearchClient(
        search_api=SearchAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
        ),
    )


def create_async_client(
    secret_key: str,
    user_agent: str,
) -> AsyncSearchClient:
    env = env_from_vars()
    return AsyncSearchClient(
        search_api=AsyncSearchAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
        ),
    )


class AsyncSearchClient:
    search_api: AsyncSearchAPI

    def __init__(
        self,
        search_api: AsyncSearchAPI,
    ):
        self.search_api = search_api

    async def search(
        self,
        q: str,
        size: int | None = None,
        next_token: str | None = None,
        properties: list[str] | None = None,
    ) -> PagedSearchResultResponse:
        """
        Search for content across the TollBit platform.

        Args:
            q: Search query string (required)
            size: Number of results to return. Maximum value is 20.
            next_token: Token for pagination. If provided, continues from the encoded page.
            properties: List of domains (max 20) to boost in search results. When provided,
                       generates a custom goggle string.

        Returns:
            PagedSearchResultResponse containing search results and next token for pagination.
        """
        properties_str: str | None = None
        if properties is not None:
            if len(properties) > 20:
                raise ValueError("Maximum of 20 properties allowed")
            properties_str = ",".join(properties)

        logger.debug(
            "Searching for content",
            extra={"q": q, "size": size, "next_token": next_token, "properties": properties},
        )

        return await self.search_api.search(
            q=q,
            size=size,
            next_token=next_token,
            properties=properties_str,
        )


class SearchClient:
    search_api: SearchAPI

    def __init__(
        self,
        search_api: SearchAPI,
    ):
        self.search_api = search_api

    def search(
        self,
        q: str,
        size: int | None = None,
        next_token: str | None = None,
        properties: list[str] | None = None,
    ) -> PagedSearchResultResponse:
        """
        Search for content across the TollBit platform.

        Args:
            q: Search query string (required)
            size: Number of results to return. Maximum value is 20.
            next_token: Token for pagination. If provided, continues from the encoded page.
            properties: List of domains (max 20) to boost in search results. When provided,
                       generates a custom goggle string.

        Returns:
            PagedSearchResultResponse containing search results and next token for pagination.
        """
        properties_str: str | None = None
        if properties is not None:
            if len(properties) > 20:
                raise ValueError("Maximum of 20 properties allowed")
            properties_str = ",".join(properties)

        logger.debug(
            "Searching for content",
            extra={"q": q, "size": size, "next_token": next_token, "properties": properties},
        )

        return self.search_api.search(
            q=q,
            size=size,
            next_token=next_token,
            properties=properties_str,
        )
