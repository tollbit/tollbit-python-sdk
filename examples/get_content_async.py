import os
from tollbit import currencies, licences, content_formats, use_content
from anyio import create_memory_object_stream, create_task_group, run
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream
from dataclasses import dataclass
from tollbit.use_content.client import AsyncUseContentClient

api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")


@dataclass
class DataResult:
    data_type: str
    data: any


async def run_get_html(
    client: AsyncUseContentClient, send_stream: MemoryObjectSendStream[DataResult]
):
    async with send_stream:
        data = await client.get_sanctioned_content(
            url="https://pioneervalleygazette.com/daydream",
            max_price_micros=11000000,
            currency=currencies.USD,
            license_type=licences.types.ON_DEMAND_LICENSE,
            format=content_formats.HTML,
        )
        await send_stream.send(DataResult("html", data))


async def run_get_markdown(
    client: AsyncUseContentClient, send_stream: MemoryObjectSendStream[DataResult]
):
    async with send_stream:
        data = await client.get_sanctioned_content(
            url="https://pioneervalleygazette.com/daydream",
            max_price_micros=11000000,
            currency=currencies.USD,
            license_type=licences.types.ON_DEMAND_LICENSE,
            format=content_formats.MARKDOWN,
        )
        await send_stream.send(DataResult("markdown", data))


async def print_results(receive_stream: MemoryObjectReceiveStream[DataResult]):
    async for result in receive_stream:
        data = result.data

        print("================================")
        if result.data_type == "html":
            print("HTML data:")
        elif result.data_type == "markdown":
            print("Markdown data:")

        print(f"data.content.header: {data.content.header}")
        print(f"data.content.body (first 100 chars): {data.content.body[:100]}")
        print(f"data.content.footer: {data.content.footer}")
        print(f"data.metadata.title: {data.metadata.title}")
        print(f"data.metadata.description: {data.metadata.description}")
        print(f"data.metadata.image_url: {data.metadata.image_url}")
        print(f"data.metadata.author: {data.metadata.author}")
        print(f"data.metadata.published: {data.metadata.published}")
        print(f"data.metadata.modified: {data.metadata.modified}")
        if data.rate:
            print(f"data.rate.price.price_micros: {data.rate.price.price_micros}")
            print(f"data.rate.price.currency: {data.rate.price.currency}")
            print(f"data.rate.license.id: {data.rate.license.id}")
            print(f"data.rate.license.license_type: {data.rate.license.license_type}")
            print(f"data.rate.license.license_path: {data.rate.license.license_path}")
            print(f"data.rate.license.permissions: {data.rate.license.permissions}")

        print("================================")


async def main():
    client = use_content.create_async_client(secret_key=api_key, user_agent=user_agent)
    send_stream, receive_stream = create_memory_object_stream[DataResult]()

    async with create_task_group() as tg:
        tg.start_soon(print_results, receive_stream)
        tg.start_soon(run_get_html, client, send_stream.clone())
        tg.start_soon(run_get_markdown, client, send_stream.clone())
        await send_stream.aclose()


run(main)
