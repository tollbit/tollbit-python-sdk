# In this example, we demonstrate how to use the Tollbit Python SDK
# to get content rate information for a specific URL.
from tollbit import use_content, crawl_content
import os
from dataclasses import dataclass
from anyio import create_memory_object_stream, create_task_group, run
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")


@dataclass
class AsyncRateResult:
    page: str
    rate_info: any


async def print_rate_info(receive_stream: MemoryObjectReceiveStream[AsyncRateResult]):
    async for result in receive_stream:
        rate_info = result.rate_info
        print("================================")
        print(f"Rates for page: {result.page}")
        print(f"{len(rate_info)} Content Rates:")
        for rate in rate_info:
            print("Content Rate:")
            print(f"  Price (micros): {rate.price.price_micros}")
            print(f"  Currency: {rate.price.currency}")
            print(f"  License ID: {rate.license.id}")
            print(f"  License Type: {rate.license.license_type}")
            print(f"  License Path: {rate.license.license_path}")
            print(f"  Permissions: {rate.license.permissions}")


# Get rates using either the crawl client or the use client
async def get_rates_use_client(
    client: use_content.AsyncUseContentClient,
    page: str,
    send_stream: MemoryObjectSendStream[AsyncRateResult],
):
    async with send_stream:
        rate_info = await client.get_rate(url=page)
        await send_stream.send(AsyncRateResult(page, rate_info))


async def get_rates_crawl_client(
    client: crawl_content.AsyncCrawlContentClient,
    page: str,
    send_stream: MemoryObjectSendStream[AsyncRateResult],
):
    async with send_stream:
        rate_info = await client.get_rate(url=page)
        await send_stream.send(AsyncRateResult(page, rate_info))


async def main():
    use = use_content.create_async_client(secret_key=api_key, user_agent=user_agent)
    crawl = crawl_content.create_async_client(secret_key=api_key, user_agent=user_agent)
    send_stream, receive_stream = create_memory_object_stream[AsyncRateResult]()

    async with create_task_group() as tg:
        tg.start_soon(print_rate_info, receive_stream)
        tg.start_soon(
            get_rates_use_client,
            use,
            "https://pioneervalleygazette.com/daydream",
            send_stream.clone(),
        )
        tg.start_soon(
            get_rates_use_client,
            use,
            "https://pioneervalleygazette.com/dragon",
            send_stream.clone(),
        )
        tg.start_soon(
            get_rates_crawl_client,
            crawl,
            "https://pioneervalleygazette.com/leaf-fortune",
            send_stream.clone(),
        )

        await send_stream.aclose()


run(main)
