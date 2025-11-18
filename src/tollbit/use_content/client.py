from __future__ import annotations
from .types import ContentRate
from tollbit.tokens import TollbitToken
from typing import Any
from tollbit._apis.content_api import ContentAPI
from tollbit._apis.token_api import TokenAPI
from urllib.parse import urlparse
from tollbit._apis.models import CreateSubdomainAccessTokenRequest, DeveloperContentResponseSuccess
from tollbit.content_formats import Format
from tollbit.currencies import Currency
from tollbit.licences import LicenceType
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
    )


class UseContentClient:
    content_api: ContentAPI
    token_api: TokenAPI

    def __init__(
        self,
        content_api: ContentAPI,
        token_api: TokenAPI,
    ):
        self.content_api = content_api
        self.token_api = token_api

    def get_rate(self, url: str) -> list[ContentRate]:
        parsed_url = urlparse(url)
        return self.content_api.get_rate(f"{parsed_url.netloc}{parsed_url.path}")

    def get_sanctioned_content(
        self,
        url: str,
        max_price_micros: int,
        currency: Currency,
        license_type: LicenceType,
        license_id: str | None = None,
        format: Format = Format.markdown,
    ) -> DeveloperContentResponseSuccess:
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
            format=format,
        )
        token_resp = self.token_api.get_content_token(req)
        token: TollbitToken = TollbitToken(token_resp.token)

        results = self.content_api.get_content(
            content_url=f"{parsed_url.netloc}{parsed_url.path}", token=token
        )

        return results[0]
