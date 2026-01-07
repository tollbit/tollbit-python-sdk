from __future__ import annotations
from tollbit.tokens import TollbitToken
from tollbit._apis.content_api import ContentAPI, AsyncContentAPI
from tollbit._apis.token_api import TokenAPI, AsyncTokenAPI
from tollbit._apis.content_retrieval_api import ContentRetrievalAPI, AsyncContentRetrievalAPI
from urllib.parse import urlparse
from tollbit._apis.models import (
    CreateCrawlAccessTokenRequest,
    CatalogResponse,
    GetContentResponse,
)
from tollbit.content_formats import Format
from pydantic import AnyUrl
from tollbit._environment import env_from_vars
from tollbit._logging import get_sdk_logger
from tollbit.forgiving_urls import parse_url_with_forgiveness

logger = get_sdk_logger(__name__)


def create_client(
    secret_key: str,
    user_agent: str,
) -> CrawlContentClient:
    env = env_from_vars()

    return CrawlContentClient(
        content_api=ContentAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
        ),
        token_api=TokenAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
        ),
        content_retrieval_api=ContentRetrievalAPI(
            user_agent=user_agent,
            env=env,
        ),
    )


def create_async_client(
    secret_key: str,
    user_agent: str,
) -> AsyncCrawlContentClient:
    env = env_from_vars()
    return AsyncCrawlContentClient(
        token_api=AsyncTokenAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
        ),
        content_retrieval_api=AsyncContentRetrievalAPI(
            user_agent=user_agent,
            env=env,
        ),
        content_api=AsyncContentAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
        ),
    )


class AsyncCrawlContentClient:
    content_retrieval_api: AsyncContentRetrievalAPI
    token_api: AsyncTokenAPI
    content_api: AsyncContentAPI

    def __init__(
        self,
        token_api: AsyncTokenAPI,
        content_retrieval_api: AsyncContentRetrievalAPI,
        content_api: AsyncContentAPI,
    ):
        self.token_api = token_api
        self.content_retrieval_api = content_retrieval_api
        self.content_api = content_api

    async def crawl_content(
        self,
        url: str,
        format: Format = Format.markdown,
    ) -> GetContentResponse:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            parsed_url = parsed_url._replace(scheme="https")

        req = CreateCrawlAccessTokenRequest(
            url=f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",  # type: ignore
            userAgent=self.token_api.user_agent,
        )
        token_resp = await self.token_api.get_crawl_token(req)
        token: TollbitToken = TollbitToken(token_resp.token)

        response = await self.content_retrieval_api.get_content(
            content_url=f"{parsed_url.netloc}{parsed_url.path}", token=token, format=format
        )

        return response

    async def list_content_catalog(
        self,
        url: str,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> CatalogResponse | None:
        parsed_url = parse_url_with_forgiveness(url)
        logger.debug(
            f"Fetching content catalog {parsed_url.netloc}",
            extra={"url": url, "page_size": page_size, "page_token": page_token},
        )
        results = await self.content_api.get_content_catalog(
            content_domain=f"{parsed_url.netloc}",
            page_size=page_size,
            page_token=page_token,
        )

        if len(results.pages) == 0:
            return None

        return results


class CrawlContentClient:
    content_api: ContentAPI
    token_api: TokenAPI
    content_retrieval_api: ContentRetrievalAPI

    def __init__(
        self,
        content_api: ContentAPI,
        token_api: TokenAPI,
        content_retrieval_api: ContentRetrievalAPI,
    ):
        self.content_api = content_api
        self.token_api = token_api
        self.content_retrieval_api = content_retrieval_api

    def list_content_catalog(
        self,
        url: str,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> CatalogResponse | None:
        parsed_url = parse_url_with_forgiveness(url)
        logger.debug(
            f"Fetching content catalog {parsed_url.netloc}",
            extra={"url": url, "page_size": page_size, "page_token": page_token},
        )
        results = self.content_api.get_content_catalog(
            content_domain=f"{parsed_url.netloc}",
            page_size=page_size,
            page_token=page_token,
        )

        if len(results.pages) == 0:
            return None

        return results

    def crawl_content(
        self,
        url: str,
        format: Format = Format.markdown,
    ) -> GetContentResponse:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            parsed_url = parsed_url._replace(scheme="https")

        req = CreateCrawlAccessTokenRequest(
            url=f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",  # type: ignore
            userAgent=self.token_api.user_agent,
        )
        token_resp = self.token_api.get_crawl_token(req)
        token: TollbitToken = TollbitToken(token_resp.token)

        response = self.content_retrieval_api.get_content(
            content_url=f"{parsed_url.netloc}{parsed_url.path}", token=token, format=format
        )

        return response
