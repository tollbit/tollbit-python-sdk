import requests
from pydantic import BaseModel, TypeAdapter
from typing import Type, TypeVar, Any
from tollbit._environment import Environment
from tollbit.content_formats import Format
from tollbit._apis.models import (
    DeveloperRateResponse,
    DeveloperContentCatalogResponse,
)
from tollbit._apis.errors import (
    ApiError,
    UnauthorizedError,
    BadRequestError,
    ServerError,
    UnknownError,
)

from tollbit._logging import get_sdk_logger

_GET_RATE_PATH = "/dev/v2/rate/<PATH>"
_GET_CATALOG_PATH = "/dev/v1/content/<DOMAIN>/catalog/list"

# Configure logging
logger = get_sdk_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class ContentAPI:
    api_key: str
    user_agent: str
    _base_url: str

    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self.api_key = api_key
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    def get_rate(self, content: str) -> list[DeveloperRateResponse]:
        try:
            headers = {"User-Agent": self.user_agent, "TollbitKey": self.api_key}
            url = f"{self._base_url}{_GET_RATE_PATH.replace('<PATH>', content)}"
            logger.debug(
                "Requesting content rate...",
                extra={"content": content, "url": url, "headers": headers},
            )
            response = requests.get(
                url,
                headers=headers,
            )
        except requests.RequestException as e:
            logger.error(f"Error occurred while fetching rate: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        logger.debug("Raw response", extra={"response_text": response.text})

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(str(err))
            raise err

        resp: list[DeveloperRateResponse] = TypeAdapter(
            list[DeveloperRateResponse]
        ).validate_python(response.json())
        return resp

    def get_content_catalog(
        self,
        content_domain: str,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> list[DeveloperContentCatalogResponse]:
        try:
            headers = {"User-Agent": self.user_agent, "TollbitKey": self.api_key}
            url = f"{self._base_url}{_GET_CATALOG_PATH.replace('<DOMAIN>', content_domain)}"
            params: dict[str, str | int] = {"pageSize": page_size}
            if page_token:
                params["pageToken"] = page_token

            url_with_params = requests.Request("GET", url, params=params).prepare().url
            if url_with_params is None:
                logger.error(
                    "Failed to prepare URL with parameters", extra={"url": url, "params": params}
                )
                raise ValueError("Failed to prepare URL with parameters")

            logger.debug(
                "Requesting content catalog...",
                extra={"url": url_with_params, "headers": headers},
            )

            response = requests.get(
                url_with_params,
                headers=headers,
            )
            logger.debug(
                "Received content catalog response",
                extra={"status_code": response.status_code, "response_text": response.text},
            )

        except requests.RequestException as e:
            logger.error(f"Error occurred while fetching content catalog: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        match response.status_code:
            case 200:
                resp: list[DeveloperContentCatalogResponse] = TypeAdapter(
                    list[DeveloperContentCatalogResponse]
                ).validate_python(response.json())
                return resp
            case 401:
                logger.error(f"HTTP ERROR {response.status_code}: {response.text}")
                raise UnauthorizedError("Unauthorized: Invalid API key")
            case 400:
                logger.error(f"HTTP ERROR {response.status_code}: {response.text}")
                raise BadRequestError(
                    "Bad Request: Check your request; most likely the content domain is invalid or unknown."
                )
            case code if 500 <= code <= 599:
                logger.error(f"HTTP ERROR {response.status_code}: {response.text}")
                raise ServerError(f"An error occurred on Tollbit's servers: {response.status_code}")
            case _:
                logger.error(f"HTTP ERROR {response.status_code}: {response.text}")
                raise UnknownError(f"An unknown error occurred: {response.status_code}")

        return []  # Shouldn't get here
