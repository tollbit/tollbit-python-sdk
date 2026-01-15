from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any

# Environement configurations
_DEVELOPER_API_BASE_URL_ENV = "TOLLBIT_SDK_DEVELOPER_API_BASE_URL"
_DEFAULT_DEVELOPER_API_BASE_URL = "https://gateway.tollbit.com"
_ANYIO_BACKEND = "TOLLBIT_SDK_ANYIO_BACKEND"
_DEFAULT_ANYIO_BACKEND = "asyncio"
_TIMEOUT_ENV = "TOLLBIT_SDK_REQUESTS_TIMEOUT"
_DEFAULT_TIMEOUT = 5.0


@dataclass(frozen=True)
class Environment:
    developer_api_base_url: str
    anyio_backend: str
    timeout: float

    def override(self, **kwargs: Any) -> Environment:
        """
        Create a new Environment instance with values overridden by keyword arguments.

        Parameters:
            **kwargs: Arbitrary keyword arguments corresponding to Environment fields.
                Supported keys include:
                    - developer_api_base_url (str): Override the API base URL.
                    - anyio_backend (str): Override the async backend.
                    - timeout (float | int): Override the timeout value.

        Returns:
            Environment: A new Environment instance with updated values.
        """
        """Create a new Environment with overridden values."""
        return Environment(
            developer_api_base_url=kwargs.get(
                "developer_api_base_url", self.developer_api_base_url
            ),
            anyio_backend=kwargs.get("anyio_backend", self.anyio_backend),
            timeout=kwargs.get("timeout", self.timeout),
        )


def env_from_vars() -> Environment:
    """Create an Environment from environment variables."""
    developer_api_base_url = os.getenv(_DEVELOPER_API_BASE_URL_ENV, _DEFAULT_DEVELOPER_API_BASE_URL)
    anyio_backend = os.getenv(_ANYIO_BACKEND, _DEFAULT_ANYIO_BACKEND)
    timeout = float(os.getenv(_TIMEOUT_ENV, _DEFAULT_TIMEOUT))
    return Environment(
        developer_api_base_url=developer_api_base_url, anyio_backend=anyio_backend, timeout=timeout
    )
