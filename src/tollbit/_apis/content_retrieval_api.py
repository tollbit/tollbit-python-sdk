import requests
import httpx
import anyio
from pydantic import TypeAdapter
from tollbit._environment import Environment
from tollbit.content_formats import Format
from tollbit._apis.models import (
    GetContentResponse,
)
from tollbit._apis.errors import (
    ServerError,
    ApiError,
)
from tollbit.tokens import TollbitToken
from tollbit._logging import get_sdk_logger

_GET_CONTENT_PATH = "/dev/v2/content/<PATH>"

# Configure logging
logger = get_sdk_logger(__name__)


class AsyncContentRetrievalAPI:
    user_agent: str
    _base_url: str

    def __init__(self, user_agent: str, env: Environment):
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    async def get_content(
        self, token: TollbitToken, content_url: str, format: Format
    ) -> GetContentResponse:
        # Implementation for fetching content using the provided token
        try:
            headers = {
                "User-Agent": self.user_agent,
                "Tollbit-Token": str(token),
                "Tollbit-Accept-Content": format.value.header_string,
            }
            url = f"{self._base_url}{_GET_CONTENT_PATH.replace('<PATH>', content_url)}"
            logger.debug(
                "Requesting content...",
                extra={"url": url, "headers": headers},
            )

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                )
            logger.debug(
                "Received content response",
                extra={"status_code": response.status_code, "response_text": response.text},
            )
        except httpx.RequestError as e:
            logger.error(f"Error occurred while fetching content: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(str(err))
            raise err

        data = response.json()
        logger.debug("Parsing get content response", extra={"response": data})
        return TypeAdapter(GetContentResponse).validate_python(data)


class ContentRetrievalAPI:
    def __init__(self, user_agent: str, env: Environment):
        self._async_api = AsyncContentRetrievalAPI(user_agent, env)
        self._env = env

    def get_content(
        self, token: TollbitToken, content_url: str, format: Format
    ) -> GetContentResponse:
        return anyio.run(
            self._async_api.get_content, token, content_url, format, backend=self._env.anyio_backend
        )
