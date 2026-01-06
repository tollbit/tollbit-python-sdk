# Crawling Content
# Crawling content is intended for discovering content offered by our partners. It is not
# intended for use with the end-user.

from tollbit import crawl_content
from tollbit import content_formats
import os
import anyio
from dataclasses import dataclass
from anyio import create_memory_object_stream, create_task_group, run
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream


@dataclass
class ScrapedData:
    format: str
    data: any


# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")


async def list_content_catalog(client):
    paged_results = await client.list_content_catalog(
        url="https://pioneervalleygazette.com",
        page_size=5,
    )

    print("Content Catalog Results (first page):")
    for page in paged_results.pages:
        print(f"page.property_id: {page.property_id}")
        print(f"page.page_url: {page.page_url}")
        print("page.last_mod:", page.last_mod)
        print("-----")

    second_page = await client.list_content_catalog(
        url="https://pioneervalleygazette.com",
        page_size=5,
        page_token=paged_results.page_token,
    )

    print("Content Catalog Results (second page):")
    print([page.property_id for page in second_page.pages])


async def handle_crawled_content(client, send_stream: MemoryObjectReceiveStream[ScrapedData]):
    async with send_stream:
        async for scraped_data in send_stream:
            data = scraped_data.data
            print("================================")
            if scraped_data.format == "html":
                print("HTML data:")
            elif scraped_data.format == "markdown":
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


async def run_get_html(
    client: crawl_content.AsyncCrawlContentClient, send_stream: MemoryObjectSendStream[ScrapedData]
):
    async with send_stream:
        data = await client.crawl_content(
            url="https://pioneervalleygazette.com/daydream",
            format=content_formats.HTML,
        )
        await send_stream.send(ScrapedData("html", data))


async def run_get_markdown(
    client: crawl_content.AsyncCrawlContentClient, send_stream: MemoryObjectSendStream[ScrapedData]
):
    async with send_stream:
        data = await client.crawl_content(
            url="https://pioneervalleygazette.com/daydream",
        )
        await send_stream.send(ScrapedData("markdown", data))


async def main():
    client = crawl_content.create_async_client(secret_key=api_key, user_agent=user_agent)
    await list_content_catalog(client)

    send_stream, receive_stream = create_memory_object_stream[ScrapedData]()
    async with create_task_group() as tg:
        tg.start_soon(handle_crawled_content, client, receive_stream)
        tg.start_soon(run_get_markdown, client, send_stream.clone())
        tg.start_soon(run_get_html, client, send_stream.clone())
        await send_stream.aclose()


run(main)
