import pytest
import httpx
from tollbit._apis.search_api import AsyncSearchAPI


@pytest.mark.anyio
async def test_search_sends_filters_only_when_set(respx_mock, test_env):
    route = respx_mock.get(f"{test_env.developer_api_base_url}/dev/v2/search").mock(
        return_value=httpx.Response(200, json={"nextToken": "", "items": []})
    )
    client = AsyncSearchAPI(api_key="test-secret-key", user_agent="test-agent", env=test_env)

    await client.search("ai", allowed_only=True, ready_to_license=False)
    await client.search("ai")

    assert dict(route.calls[0].request.url.params) == {
        "q": "ai",
        "allowedOnly": "true",
        "readyToLicense": "false",
    }
    assert dict(route.calls[1].request.url.params) == {"q": "ai"}
