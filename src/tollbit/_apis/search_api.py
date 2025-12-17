from __future__ import annotations

import requests
from pydantic import TypeAdapter
from tollbit._environment import Environment
from tollbit._apis.models._generated.openapi_tollbit_apis import PagedSearchResultResponse
from tollbit._apis.errors import (
    ServerError,
    ApiError,
)
from tollbit._logging import get_sdk_logger

_SEARCH_PATH = "/dev/v2/search"

logger = get_sdk_logger(__name__)


class SearchAPI:
    api_key: str
    user_agent: str
    _base_url: str

    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self.api_key = api_key
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    def search(
        self,
        q: str,
        size: int | None = None,
        next_token: str | None = None,
        properties: str | None = None,
    ) -> PagedSearchResultResponse:
        try:
            headers = {"User-Agent": self.user_agent, "TollbitKey": self.api_key}
            url = f"{self._base_url}{_SEARCH_PATH}"
            params: dict[str, str | int] = {"q": q}
            if size is not None:
                params["size"] = size
            if next_token is not None:
                params["next-token"] = next_token
            if properties is not None:
                params["properties"] = properties

            url_with_params = requests.Request("GET", url, params=params).prepare().url
            if url_with_params is None:
                logger.error(
                    "Failed to prepare URL with parameters", extra={"url": url, "params": params}
                )
                raise ValueError("Failed to prepare URL with parameters")

            logger.debug(
                "Requesting search results...",
                extra={"url": url_with_params, "headers": headers},
            )

            response = requests.get(
                url_with_params,
                headers=headers,
            )
            logger.debug(
                "Received search response",
                extra={"status_code": response.status_code, "response_text": response.text},
            )

        except requests.RequestException as e:
            logger.error(f"Error occurred while searching: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(str(err))
            raise err

        resp: PagedSearchResultResponse = TypeAdapter(PagedSearchResultResponse).validate_python(
            response.json()
        )
        return resp
