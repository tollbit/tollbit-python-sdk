import requests
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


class ContentRetrievalAPI:
    user_agent: str
    _base_url: str

    def __init__(self, user_agent: str, env: Environment):
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url

    def get_content(
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
            response = requests.get(
                url,
                headers=headers,
            )
            logger.debug(
                "Received content response",
                extra={"status_code": response.status_code, "response_text": response.text},
            )
        except requests.RequestException as e:
            logger.error(f"Error occurred while fetching content: {e}")
            raise ServerError("Unable to connect to the Tollbit server") from e

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(str(err))
            raise err

        data = response.json()
        logger.debug("Parsing get content response", extra={"response": data})
        return TypeAdapter(GetContentResponse).validate_python(data)
