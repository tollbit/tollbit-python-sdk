import pytest
from tollbit._environment import Environment


@pytest.fixture
def test_env():
    return Environment(developer_api_base_url="http://testserver.local")
