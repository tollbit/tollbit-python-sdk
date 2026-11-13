from __future__ import annotations
from datetime import date, datetime
from tollbit.tokens import TollbitToken
from tollbit._apis.content_api import ContentAPI, AsyncContentAPI
from tollbit._apis.token_api import TokenAPI, AsyncTokenAPI
from tollbit._apis.content_retrieval_api import ContentRetrievalAPI, AsyncContentRetrievalAPI
from urllib.parse import urlparse
from tollbit._apis.models import (
    CreateCrawlAccessTokenRequest,
    CatalogResponse,
    GetContentResponse,
    DeveloperRateResponse,
    BatchRateResponseV2,
    PagedPropertyListResponse,
)
from tollbit.content_formats import Format
from tollbit._environment import env_from_vars
from tollbit._http import AsyncClientContext, HTTPTransport, SyncClientContext
from tollbit._logging import get_sdk_logger
from tollbit.forgiving_urls import content_urls, parse_url_with_forgiveness

logger = get_sdk_logger(__name__)


def create_client(
    secret_key: str,
    user_agent: str,
    request_timeout: float | None = None,
) -> CrawlContentClient:
    env = env_from_vars()

    if request_timeout is not None:
        env = env.override(timeout=request_timeout)

    http = HTTPTransport(env)
    return CrawlContentClient(
        _http=http,
        content_api=ContentAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
            http=http,
        ),
        token_api=TokenAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
            http=http,
        ),
        content_retrieval_api=ContentRetrievalAPI(
            user_agent=user_agent,
            env=env,
            http=http,
        ),
    )


def create_async_client(
    secret_key: str,
    user_agent: str,
    request_timeout: float | None = None,
) -> AsyncCrawlContentClient:
    env = env_from_vars()

    if request_timeout is not None:
        env = env.override(timeout=request_timeout)

    http = HTTPTransport(env)
    return AsyncCrawlContentClient(
        _http=http,
        token_api=AsyncTokenAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
            http=http,
        ),
        content_retrieval_api=AsyncContentRetrievalAPI(
            user_agent=user_agent,
            env=env,
            http=http,
        ),
        content_api=AsyncContentAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
            http=http,
        ),
    )


class AsyncCrawlContentClient(AsyncClientContext):
    content_retrieval_api: AsyncContentRetrievalAPI
    token_api: AsyncTokenAPI
    content_api: AsyncContentAPI

    def __init__(
        self,
        token_api: AsyncTokenAPI,
        content_retrieval_api: AsyncContentRetrievalAPI,
        content_api: AsyncContentAPI,
        *,
        _http: HTTPTransport | None = None,
    ):
        super().__init__(_http)
        self.token_api = token_api
        self.content_retrieval_api = content_retrieval_api
        self.content_api = content_api

    async def crawl_content(
        self,
        url: str,
        format: Format = Format.markdown,
    ) -> GetContentResponse:
        token_url, retrieval_url = content_urls(url)
        req = CreateCrawlAccessTokenRequest(
            url=token_url,  # type: ignore
            userAgent=self.token_api.user_agent,
        )
        token_resp = await self.token_api.get_crawl_token(req)
        token: TollbitToken = TollbitToken(token_resp.token)

        response = await self.content_retrieval_api.get_content(
            content_url=retrieval_url, token=token, format=format
        )

        return response

    async def list_content_catalog(
        self,
        url: str,
        page_size: int = 100,
        page_token: str | None = None,
        *,
        modified_from: date | datetime | None = None,
        modified_to: date | datetime | None = None,
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
            modified_from=modified_from,
            modified_to=modified_to,
        )

        if len(results.pages) == 0:
            return None

        return results

    async def list_properties(
        self,
        page_size: int = 100,
        page_token: str | None = None,
        *,
        ready_to_license: bool | None = None,
        added_from: date | datetime | None = None,
        added_to: date | datetime | None = None,
    ) -> PagedPropertyListResponse:
        return await self.content_api.list_properties(
            page_size,
            page_token,
            ready_to_license=ready_to_license,
            added_from=added_from,
            added_to=added_to,
        )

    async def get_rate(
        self, url: str, *, custom_license_ids: list[str] | None = None
    ) -> list[DeveloperRateResponse]:
        parsed_url = urlparse(url)
        return await self.content_api.get_rate(
            f"{parsed_url.netloc}{parsed_url.path}", custom_license_ids=custom_license_ids
        )

    async def get_rates(
        self, urls: list[str], *, custom_license_ids: list[str] | None = None
    ) -> list[BatchRateResponseV2]:
        return await self.content_api.get_rates(urls, custom_license_ids=custom_license_ids)


class CrawlContentClient(SyncClientContext):
    content_api: ContentAPI
    token_api: TokenAPI
    content_retrieval_api: ContentRetrievalAPI

    def __init__(
        self,
        content_api: ContentAPI,
        token_api: TokenAPI,
        content_retrieval_api: ContentRetrievalAPI,
        *,
        _http: HTTPTransport | None = None,
    ):
        super().__init__(_http)
        self.content_api = content_api
        self.token_api = token_api
        self.content_retrieval_api = content_retrieval_api

    def list_content_catalog(
        self,
        url: str,
        page_size: int = 100,
        page_token: str | None = None,
        *,
        modified_from: date | datetime | None = None,
        modified_to: date | datetime | None = None,
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
            modified_from=modified_from,
            modified_to=modified_to,
        )

        if len(results.pages) == 0:
            return None

        return results

    def crawl_content(
        self,
        url: str,
        format: Format = Format.markdown,
    ) -> GetContentResponse:
        token_url, retrieval_url = content_urls(url)
        req = CreateCrawlAccessTokenRequest(
            url=token_url,  # type: ignore
            userAgent=self.token_api.user_agent,
        )
        token_resp = self.token_api.get_crawl_token(req)
        token: TollbitToken = TollbitToken(token_resp.token)

        response = self.content_retrieval_api.get_content(
            content_url=retrieval_url, token=token, format=format
        )

        return response

    def list_properties(
        self,
        page_size: int = 100,
        page_token: str | None = None,
        *,
        ready_to_license: bool | None = None,
        added_from: date | datetime | None = None,
        added_to: date | datetime | None = None,
    ) -> PagedPropertyListResponse:
        return self.content_api.list_properties(
            page_size,
            page_token,
            ready_to_license=ready_to_license,
            added_from=added_from,
            added_to=added_to,
        )

    def get_rate(
        self, url: str, *, custom_license_ids: list[str] | None = None
    ) -> list[DeveloperRateResponse]:
        parsed_url = urlparse(url)
        return self.content_api.get_rate(
            f"{parsed_url.netloc}{parsed_url.path}", custom_license_ids=custom_license_ids
        )

    def get_rates(
        self, urls: list[str], *, custom_license_ids: list[str] | None = None
    ) -> list[BatchRateResponseV2]:
        return self.content_api.get_rates(urls, custom_license_ids=custom_license_ids)
