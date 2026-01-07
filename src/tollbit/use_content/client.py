from __future__ import annotations
from tollbit.tokens import TollbitToken
from tollbit._apis.content_api import ContentAPI, AsyncContentAPI
from tollbit._apis.token_api import TokenAPI, AsyncTokenAPI
from tollbit._apis.content_retrieval_api import ContentRetrievalAPI, AsyncContentRetrievalAPI
from urllib.parse import urlparse
from tollbit._apis.models import (
    CreateSubdomainAccessTokenRequest,
    GetContentResponse,
    DeveloperRateResponse,
)
from tollbit.content_formats import Format
from tollbit.currencies import Currency
from tollbit.licenses.types import LicenseType
from pydantic import AnyUrl
from tollbit._environment import env_from_vars


def create_client(
    secret_key: str,
    user_agent: str,
) -> UseContentClient:
    env = env_from_vars()

    return UseContentClient(
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
) -> AsyncUseContentClient:
    env = env_from_vars()

    return AsyncUseContentClient(
        token_api=AsyncTokenAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
        ),
        content_api=AsyncContentAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
        ),
        content_retrieval_api=AsyncContentRetrievalAPI(
            user_agent=user_agent,
            env=env,
        ),
    )


class AsyncUseContentClient:
    content_retrieval_api: AsyncContentRetrievalAPI
    token_api: AsyncTokenAPI
    content_api: AsyncContentAPI

    def __init__(
        self,
        token_api: AsyncTokenAPI,
        content_api: AsyncContentAPI,
        content_retrieval_api: AsyncContentRetrievalAPI,
    ):
        self.token_api = token_api
        self.content_api = content_api
        self.content_retrieval_api = content_retrieval_api

    async def get_sanctioned_content(
        self,
        url: str,
        max_price_micros: int,
        currency: Currency,
        license_type: LicenseType,
        license_id: str | None = None,
        format: Format = Format.markdown,
    ) -> GetContentResponse:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            parsed_url = parsed_url._replace(scheme="https")

        req = CreateSubdomainAccessTokenRequest(
            url=f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",  # type: ignore
            userAgent=self.token_api.user_agent,
            maxPriceMicros=max_price_micros,
            currency=currency.value,
            licenseType=license_type.value,
            licenseCuid=license_id or "",
        )
        token_resp = await self.token_api.get_content_token(req)
        token: TollbitToken = TollbitToken(token_resp.token)

        response = await self.content_retrieval_api.get_content(
            content_url=f"{parsed_url.netloc}{parsed_url.path}", token=token, format=format
        )

        return response

    async def get_rate(self, url: str) -> list[DeveloperRateResponse]:
        parsed_url = urlparse(url)
        return await self.content_api.get_rate(f"{parsed_url.netloc}{parsed_url.path}")


class UseContentClient:
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

    def get_rate(self, url: str) -> list[DeveloperRateResponse]:
        parsed_url = urlparse(url)
        return self.content_api.get_rate(f"{parsed_url.netloc}{parsed_url.path}")

    def get_sanctioned_content(
        self,
        url: str,
        max_price_micros: int,
        currency: Currency,
        license_type: LicenseType,
        license_id: str | None = None,
        format: Format = Format.markdown,
    ) -> GetContentResponse:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            parsed_url = parsed_url._replace(scheme="https")

        req = CreateSubdomainAccessTokenRequest(
            url=f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",  # type: ignore
            userAgent=self.token_api.user_agent,
            maxPriceMicros=max_price_micros,
            currency=currency.value,
            licenseType=license_type.value,
            licenseCuid=license_id or "",
        )
        token_resp = self.token_api.get_content_token(req)
        token: TollbitToken = TollbitToken(token_resp.token)

        response = self.content_retrieval_api.get_content(
            content_url=f"{parsed_url.netloc}{parsed_url.path}", token=token, format=format
        )

        return response
