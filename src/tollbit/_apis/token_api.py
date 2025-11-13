import requests
import os
from pydantic import BaseModel, TypeAdapter
from typing import Type, TypeVar, Any
from tollbit._environment import Environment
import logging
from tollbit._apis.models import (
    CreateSubdomainAccessTokenRequest,
    CreateSubdomainAccessTokenResponse,
    CreateCrawlAccessTokenRequest,
    CreateCrawlAccessTokenResponse,
    Format,
    Error,
)
from tollbit._apis.errors import (
    UnauthorizedError,
    BadRequestError,
    ServerError,
    UnknownError,
)
from tollbit._environment import Environment
from tollbit._logging import get_sdk_logger

CREATE_CONTENT_TOKEN_PATH = "/dev/v2/tokens/content"
CREATE_CRAWL_TOKEN_PATH = "/dev/v2/tokens/crawl"

# Configure logging
logger = get_sdk_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class TokenAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self.api_key = api_key
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    def get_content_token(
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
            response = self._post_model(CREATE_CONTENT_TOKEN_PATH, self._headers(), req)
        except requests.ConnectionError as e:
            logger.error(f"Connection error occurred: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        return _handle_response(response, CreateSubdomainAccessTokenResponse)

    def get_crawl_token(self, req: CreateCrawlAccessTokenRequest) -> CreateCrawlAccessTokenResponse:

        logger.debug(
            "Requesting crawl access token...",
            extra={
                "request": req.model_dump(),
                "url": f"{self._base_url}{CREATE_CRAWL_TOKEN_PATH}",
                "headers": self._headers(),
            },
        )
        try:
            response = self._post_model(CREATE_CRAWL_TOKEN_PATH, self._headers(), req)
        except requests.ConnectionError as e:
            logger.error(f"Connection error occurred: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        return _handle_response(response, CreateCrawlAccessTokenResponse)

    def _post_model(self, path: str, headers: dict[str, str], body: BaseModel) -> requests.Response:
        payload = body.model_dump(mode="json")
        response = requests.post(f"{self._base_url}{path}", headers=headers, json=payload)
        return response

    def _headers(self) -> dict[str, str]:
        return {
            "TollbitKey": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }


def _handle_response(response: requests.Response, success_model: Type[T]) -> T:
    match response.status_code:
        case 200:
            result: T = TypeAdapter(success_model).validate_python(response.json())
            return result
        case 401:
            logger.error(f"HTTP ERROR {response.status_code}: {response.text}")
            raise UnauthorizedError("Unauthorized: Invalid API key")
        case 400:
            logger.error(f"HTTP ERROR {response.status_code}: {response.text}")
            raise BadRequestError(
                "Bad Request: Check your request details; most likely an invalid domain."
            )
        case code if 500 <= code <= 599:
            logger.error(f"HTTP ERROR {response.status_code}: {response.text}")
            raise ServerError(f"An error occurred on Tollbit's servers: {response.status_code}")
        case _:
            logger.error(f"HTTP ERROR {response.status_code}: {response.text}")
            raise UnknownError(f"An unknown error occurred: {response.status_code}")
