# Crawling Content
# Crawling content is intended for discovering content offered by our partners. It is not
# intended for use with the end-user.

from tollbit import crawl_content
from tollbit import content_formats
import os

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")

client = crawl_content.create_client(secret_key=api_key, user_agent=user_agent)

# Content Catalog Example
# This example shows how to use the crawl_content client to retrieve the content catalog for
# a particular property.

paged_results = client.list_content_catalog(
    url="https://pioneervalleygazette.com",
    page_size=5,
)

print("Content Catalog Results (first page):")
for page in paged_results.pages:
    print(f"page.property_id: {page.property_id}")
    print(f"page.page_url: {page.page_url}")
    print("page.last_mod:", page.last_mod)
    print("-----")

second_page = client.list_content_catalog(
    url="https://pioneervalleygazette.com",
    page_size=5,
    page_token=paged_results.page_token,
)

print("Content Catalog Results (second page):")
print([page.property_id for page in second_page.pages])

# In this example, we demonstrate how to use the Tollbit Python SDK
# to crawl content for a specific URL.
data = client.crawl_content(
    url="https://pioneervalleygazette.com/daydream",
)
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

data = client.crawl_content(
    url="https://pioneervalleygazette.com/daydream", format=content_formats.HTML
)
print("HTML data:")
print(f"data.content.header: {data.content.header}")
print(f"data.content.body (first 100 chars): {data.content.body[:100]}")
print(f"data.content.footer: {data.content.footer}")
