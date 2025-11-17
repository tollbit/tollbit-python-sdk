# Crawling Content
# Crawling content is intended for discovering content offered by our partners. It is not
# intended for use with the end-user.

from tollbit import crawl_content
import os

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")

client = crawl_content.create_client(secret_key=api_key, user_agent=user_agent)

# Content Catalog Example
# This example shows how to use the crawl_content client to retrieve the content catalog for
# a particular property.

paged_results = client.get_content_catalog(
    url="https://pioneervalleygazette.com",
    page_size=5,
)

print("Content Catalog Results (first page):")
print([paged.model_dump() for paged in paged_results.contents])

second_page = client.get_content_catalog(
    url="https://pioneervalleygazette.com",
    page_size=5,
    page_token=paged_results.next_page_token,
)

print("Content Catalog Results (second page):")
print([paged.model_dump() for paged in second_page.contents])
