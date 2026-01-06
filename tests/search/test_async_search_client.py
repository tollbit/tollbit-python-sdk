import pytest
from tollbit.search.client import AsyncSearchClient
from tollbit._apis.search_api import AsyncSearchAPI
from unittest.mock import AsyncMock, MagicMock
from test_helpers.stub_api_responses import stub_search_response


@pytest.mark.anyio
async def test_async_search_basic():
    fake_response = stub_search_response()
    mock_search_api = MagicMock(spec=AsyncSearchAPI)
    mock_search_api.search = AsyncMock(return_value=fake_response)

    client = AsyncSearchClient(search_api=mock_search_api)

    result = await client.search(q="python tutorial")

    mock_search_api.search.assert_awaited_once_with(
        q="python tutorial",
        size=None,
        next_token=None,
        properties=None,
    )
    assert result == fake_response
    assert len(result.items) == 2
    assert result.next_token == "next-token-123"


@pytest.mark.anyio
async def test_async_search_with_size():
    fake_response = stub_search_response()
    mock_search_api = MagicMock(spec=AsyncSearchAPI)
    mock_search_api.search = AsyncMock(return_value=fake_response)

    client = AsyncSearchClient(search_api=mock_search_api)

    result = await client.search(q="tutorial", size=10)

    mock_search_api.search.assert_awaited_once_with(
        q="tutorial",
        size=10,
        next_token=None,
        properties=None,
    )
    assert result == fake_response


@pytest.mark.anyio
async def test_async_search_with_next_token():
    fake_response = stub_search_response()
    mock_search_api = MagicMock(spec=AsyncSearchAPI)
    mock_search_api.search = AsyncMock(return_value=fake_response)

    client = AsyncSearchClient(search_api=mock_search_api)

    result = await client.search(q="tutorial", next_token="token-123")

    mock_search_api.search.assert_awaited_once_with(
        q="tutorial",
        size=None,
        next_token="token-123",
        properties=None,
    )
    assert result == fake_response


@pytest.mark.anyio
async def test_async_search_with_properties():
    fake_response = stub_search_response()
    mock_search_api = MagicMock(spec=AsyncSearchAPI)
    mock_search_api.search = AsyncMock(return_value=fake_response)

    client = AsyncSearchClient(search_api=mock_search_api)

    result = await client.search(
        q="tutorial",
        properties=["example.com", "tutorial.com"],
    )

    mock_search_api.search.assert_awaited_once_with(
        q="tutorial",
        size=None,
        next_token=None,
        properties="example.com,tutorial.com",
    )
    assert result == fake_response


@pytest.mark.anyio
async def test_async_search_with_all_parameters():
    fake_response = stub_search_response()
    mock_search_api = MagicMock(spec=AsyncSearchAPI)
    mock_search_api.search = AsyncMock(return_value=fake_response)

    client = AsyncSearchClient(search_api=mock_search_api)

    result = await client.search(
        q="python tutorial",
        size=5,
        next_token="token-456",
        properties=["example.com"],
    )

    mock_search_api.search.assert_awaited_once_with(
        q="python tutorial",
        size=5,
        next_token="token-456",
        properties="example.com",
    )
    assert result == fake_response


@pytest.mark.anyio
async def test_async_search_properties_max_limit():
    mock_search_api = MagicMock(spec=AsyncSearchAPI)
    client = AsyncSearchClient(search_api=mock_search_api)

    properties = [f"example{i}.com" for i in range(21)]

    with pytest.raises(ValueError, match="Maximum of 20 properties allowed"):
        await client.search(q="test", properties=properties)

    mock_search_api.search.assert_not_called()


@pytest.mark.anyio
async def test_async_search_properties_exactly_20():
    fake_response = stub_search_response()
    mock_search_api = MagicMock(spec=AsyncSearchAPI)
    mock_search_api.search = AsyncMock(return_value=fake_response)

    client = AsyncSearchClient(search_api=mock_search_api)

    properties = [f"example{i}.com" for i in range(20)]

    result = await client.search(q="test", properties=properties)

    mock_search_api.search.assert_awaited_once_with(
        q="test",
        size=None,
        next_token=None,
        properties=",".join(properties),
    )
    assert result == fake_response


@pytest.mark.anyio
async def test_async_search_properties_empty_list():
    fake_response = stub_search_response()
    mock_search_api = MagicMock(spec=AsyncSearchAPI)
    mock_search_api.search = AsyncMock(return_value=fake_response)

    client = AsyncSearchClient(search_api=mock_search_api)

    result = await client.search(q="test", properties=[])

    mock_search_api.search.assert_awaited_once_with(
        q="test",
        size=None,
        next_token=None,
        properties="",
    )
    assert result == fake_response
