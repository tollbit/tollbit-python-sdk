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
print([paged.model_dump() for paged in paged_results.contents])

second_page = client.list_content_catalog(
    url="https://pioneervalleygazette.com",
    page_size=5,
    page_token=paged_results.next_page_token,
)

print("Content Catalog Results (second page):")
print([paged.model_dump() for paged in second_page.contents])

# In this example, we demonstrate how to use the Tollbit Python SDK
# to crawl content for a specific URL.
data = client.crawl_content(
    url="https://pioneervalleygazette.com/daydream",
)
print("Markdown data:", data)

data = client.crawl_content(
    url="https://pioneervalleygazette.com/daydream", format=content_formats.HTML
)
print("HTML data:", data)
