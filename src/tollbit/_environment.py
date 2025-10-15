import os
from dataclasses import dataclass

# Environement configurations
_DEVELOPER_API_BASE_URL_ENV = "TOLLBIT_SDK_DEVELOPER_API_BASE_URL"
_DEFAULT_DEVELOPER_API_BASE_URL = "https://gateway.tollbit.com"


@dataclass(frozen=True)
class Environment:
    developer_api_base_url: str


def env_from_vars() -> Environment:
    """Create an Environment from environment variables."""
    developer_api_base_url = os.getenv(_DEVELOPER_API_BASE_URL_ENV, _DEFAULT_DEVELOPER_API_BASE_URL)
    return Environment(developer_api_base_url=developer_api_base_url)
