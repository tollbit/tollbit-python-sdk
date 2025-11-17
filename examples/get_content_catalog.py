# This example shows how to use the use_content client to retrieve the content catalog for
# a particular property.

from tollbit import use_content
import os


# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")

client = use_content.create_client(secret_key=api_key, user_agent=user_agent)

paged_results = client.get_content_catalog(
    url="https://pioneervalleygazette.com",
    page_size=5,
)

print("Content Catalog Results (first page):")
print([paged.model_dump() for paged in paged_results.results])

second_page = client.get_content_catalog(
    url="https://pioneervalleygazette.com",
    page_size=5,
    page_token=paged_results.next_page_token,
)

print("Content Catalog Results (second page):")
print([paged.model_dump() for paged in second_page.results])
