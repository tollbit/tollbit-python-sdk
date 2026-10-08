import functools
from datetime import date, datetime
import httpx
import anyio
from pydantic import TypeAdapter
from tollbit._environment import Environment
from tollbit._apis.models import (
    DeveloperRateResponse,
    CatalogResponse,
    BatchGetRateRequest,
    BatchRateResponseV2,
    PagedPropertyListResponse,
)
from tollbit._apis.errors import (
    ApiError,
    ServerError,
    httpx_error_details,
    api_error_details,
)
from tollbit._logging import get_sdk_logger

_GET_RATE_PATH = "/dev/v2/rates/<PATH>"
_BATCH_GET_RATES_PATH = "/dev/v2/rates/batch"
_GET_CATALOG_PATH = "/dev/v2/content/<DOMAIN>/catalog/list"
_LIST_PROPERTIES_PATH = "/dev/v2/properties"

# Configure logging
logger = get_sdk_logger(__name__)


class AsyncContentAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self.api_key = api_key
        self.user_agent = user_agent
        self._base_url = env.developer_api_base_url
        self._timeout = env.timeout

    async def get_rate(
        self, content: str, *, custom_license_ids: list[str] | None = None
    ) -> list[DeveloperRateResponse]:
        headers = self._headers()
        url = f"{self._base_url}{_GET_RATE_PATH.replace('<PATH>', content)}"
        params: dict[str, list[str]] = {}
        if custom_license_ids:
            params["customLicenseId"] = custom_license_ids
        logger.debug(
            "Requesting content rate...",
            extra={"content": content, "url": url, "headers": headers, "params": params},
        )
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=headers, params=params)
        except httpx.RequestError as e:
            logger.error(f"Couldn't fetch rate: {e!r}", extra=httpx_error_details(e))
            raise ServerError("Unable to connect to the Tollbit server") from e

        logger.debug("Raw response", extra={"response_text": response.text})

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(f"Couldn't get rate: {err!r}", extra=api_error_details(err))
            raise err

        resp: list[DeveloperRateResponse] = TypeAdapter(
            list[DeveloperRateResponse]
        ).validate_python(response.json())
        return resp

    async def get_rates(
        self, urls: list[str], *, custom_license_ids: list[str] | None = None
    ) -> list[BatchRateResponseV2]:
        headers = self._headers()
        url = f"{self._base_url}{_BATCH_GET_RATES_PATH}"
        req = BatchGetRateRequest(urls=urls, customLicenseIds=custom_license_ids)
        payload = req.model_dump(mode="json", by_alias=True, exclude_none=True)
        logger.debug(
            "Requesting batch content rates...",
            extra={"url": url, "headers": headers, "request": payload},
        )
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
        except httpx.RequestError as e:
            logger.error(f"Couldn't fetch rates: {e!r}", extra=httpx_error_details(e))
            raise ServerError("Unable to connect to the Tollbit server") from e

        logger.debug("Raw response", extra={"response_text": response.text})

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(f"Couldn't get rates: {err!r}", extra=api_error_details(err))
            raise err

        resp: list[BatchRateResponseV2] = TypeAdapter(list[BatchRateResponseV2]).validate_python(
            response.json()
        )
        return resp

    async def get_content_catalog(
        self,
        content_domain: str,
        page_size: int = 100,
        page_token: str | None = None,
        *,
        modified_from: date | datetime | None = None,
        modified_to: date | datetime | None = None,
    ) -> CatalogResponse:
        headers = self._headers()
        url = f"{self._base_url}{_GET_CATALOG_PATH.replace('<DOMAIN>', content_domain)}"
        params: dict[str, str | int] = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        if modified_from is not None:
            params["from"] = modified_from.isoformat()
        if modified_to is not None:
            params["to"] = modified_to.isoformat()

        logger.debug(
            "Requesting content catalog...",
            extra={"url": url, "headers": headers, "params": params},
        )
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=headers, params=params)
        except httpx.RequestError as e:
            logger.error(f"Couldn't fetch content catalog: {e!r}", extra=httpx_error_details(e))
            raise ServerError("Unable to connect to the Tollbit server") from e

        logger.debug(
            "Received content catalog response",
            extra={"status_code": response.status_code, "response_text": response.text},
        )

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(f"Couldn't get content catalog: {err!r}", extra=api_error_details(err))
            raise err

        resp: CatalogResponse = TypeAdapter(CatalogResponse).validate_python(response.json())
        return resp

    async def list_properties(
        self,
        page_size: int = 100,
        page_token: str | None = None,
        *,
        ready_to_license: bool | None = None,
        added_from: date | datetime | None = None,
        added_to: date | datetime | None = None,
    ) -> PagedPropertyListResponse:
        headers = self._headers()
        url = f"{self._base_url}{_LIST_PROPERTIES_PATH}"
        params: dict[str, str | int | bool] = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        if ready_to_license is not None:
            params["readyToLicense"] = ready_to_license
        if added_from is not None:
            params["from"] = added_from.isoformat()
        if added_to is not None:
            params["to"] = added_to.isoformat()

        logger.debug(
            "Requesting properties...",
            extra={"url": url, "headers": headers, "params": params},
        )
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=headers, params=params)
        except httpx.RequestError as e:
            logger.error(f"Couldn't fetch properties: {e!r}", extra=httpx_error_details(e))
            raise ServerError("Unable to connect to the Tollbit server") from e

        logger.debug(
            "Received properties response",
            extra={"status_code": response.status_code, "response_text": response.text},
        )

        if response.status_code != 200:
            err = ApiError.from_response(response)
            logger.error(f"Couldn't get properties: {err!r}", extra=api_error_details(err))
            raise err

        resp: PagedPropertyListResponse = TypeAdapter(PagedPropertyListResponse).validate_python(
            response.json()
        )
        return resp

    def _headers(self) -> dict[str, str]:
        return {
            "TollbitKey": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }


class ContentAPI:
    def __init__(self, api_key: str, user_agent: str, env: Environment):
        self._env = env
        self._async_api = AsyncContentAPI(api_key=api_key, user_agent=user_agent, env=env)

    def get_rate(
        self, content: str, *, custom_license_ids: list[str] | None = None
    ) -> list[DeveloperRateResponse]:
        return anyio.run(
            functools.partial(
                self._async_api.get_rate, content, custom_license_ids=custom_license_ids
            ),
            backend=self._env.anyio_backend,
        )

    def get_rates(
        self, urls: list[str], *, custom_license_ids: list[str] | None = None
    ) -> list[BatchRateResponseV2]:
        return anyio.run(
            functools.partial(
                self._async_api.get_rates, urls, custom_license_ids=custom_license_ids
            ),
            backend=self._env.anyio_backend,
        )

    def get_content_catalog(
        self,
        content_domain: str,
        page_size: int = 100,
        page_token: str | None = None,
        *,
        modified_from: date | datetime | None = None,
        modified_to: date | datetime | None = None,
    ) -> CatalogResponse:
        return anyio.run(
            functools.partial(
                self._async_api.get_content_catalog,
                content_domain,
                page_size,
                page_token,
                modified_from=modified_from,
                modified_to=modified_to,
            ),
            backend=self._env.anyio_backend,
        )

    def list_properties(
        self,
        page_size: int = 100,
        page_token: str | None = None,
        *,
        ready_to_license: bool | None = None,
        added_from: date | datetime | None = None,
        added_to: date | datetime | None = None,
    ) -> PagedPropertyListResponse:
        return anyio.run(
            functools.partial(
                self._async_api.list_properties,
                page_size,
                page_token,
                ready_to_license=ready_to_license,
                added_from=added_from,
                added_to=added_to,
            ),
            backend=self._env.anyio_backend,
        )
