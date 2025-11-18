from __future__ import annotations
from tollbit.tokens import TollbitToken
from tollbit._apis.content_api import ContentAPI
from tollbit._apis.token_api import TokenAPI
from urllib.parse import urlparse
from tollbit._apis.models import (
    CreateCrawlAccessTokenRequest,
    DeveloperContentCatalogResponse,
    DeveloperContentResponseSuccess,
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
    )


class CrawlContentClient:
    content_api: ContentAPI
    token_api: TokenAPI

    def __init__(
        self,
        content_api: ContentAPI,
        token_api: TokenAPI,
    ):
        self.content_api = content_api
        self.token_api = token_api

    def list_content_catalog(
        self,
        url: str,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> DeveloperContentCatalogResponse | None:
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

        if len(results) == 0:
            return None

        return results[0]

    def crawl_content(
        self,
        url: str,
        format: Format = Format.markdown,
    ) -> DeveloperContentResponseSuccess:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            parsed_url = parsed_url._replace(scheme="https")

        req = CreateCrawlAccessTokenRequest(
            url=f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",  # type: ignore
            userAgent=self.token_api.user_agent,
        )
        token_resp = self.token_api.get_crawl_token(req)
        token: TollbitToken = TollbitToken(token_resp.token)

        results = self.content_api.get_content(
            content_url=f"{parsed_url.netloc}{parsed_url.path}", token=token
        )

        return results[0]
