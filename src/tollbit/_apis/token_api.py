import requests
import os
from pydantic import BaseModel, TypeAdapter
from typing import Type, TypeVar, Any
from tollbit._environment import Environment
import logging
from tollbit._apis.models import (
    CreateSubdomainAccessTokenRequest,
    CreateSubdomainAccessTokenResponse,
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

CREATE_TOKEN_PATH = "/dev/v2/tokens/content"

# Configure logging
logger = get_sdk_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class TokenAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self.api_key = api_key
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    def get_token(
        self, req: CreateSubdomainAccessTokenRequest
    ) -> CreateSubdomainAccessTokenResponse:
        headers = {
            "TollbitKey": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }

        logger.debug(
            "Requesting subdomain access token...",
            extra={
                "request": req.model_dump(),
                "url": f"{self._base_url}{CREATE_TOKEN_PATH}",
                "headers": headers,
            },
        )
        try:
            response = self._post_model(CREATE_TOKEN_PATH, headers, req)
        except requests.ConnectionError as e:
            logger.error(f"Connection error occurred: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        match response.status_code:
            case 200:
                result: CreateSubdomainAccessTokenResponse = TypeAdapter(
                    CreateSubdomainAccessTokenResponse
                ).validate_python(response.json())
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

        return None  # Should not reach here

    def _post_model(self, path: str, headers: dict[str, str], body: BaseModel) -> requests.Response:
        payload = body.model_dump(mode="json")
        response = requests.post(f"{self._base_url}{path}", headers=headers, json=payload)
        return response
