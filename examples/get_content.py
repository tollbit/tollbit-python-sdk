# In this example, we demonstrate how to use the Tollbit Python SDK
# to get content for a specific URL.
from tollbit import use_content
from tollbit import licenses
from tollbit import currencies
from tollbit import content_formats
from tollbit import use_content
import os

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")

client = use_content.create_client(secret_key=api_key, user_agent=user_agent)


data = client.get_sanctioned_content(
    url="https://pioneervalleygazette.com/daydream",
    max_price_micros=11000000,
    currency=currencies.USD,
    license_type=licenses.types.ON_DEMAND_LICENSE,
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


data = client.get_sanctioned_content(
    url="https://pioneervalleygazette.com/daydream",
    max_price_micros=11000000,
    currency=currencies.USD,
    license_type=licenses.types.ON_DEMAND_LICENSE,
    format=content_formats.HTML,
)
print("HTML data:")
print(f"data.content.header: {data.content.header}")
print(f"data.content.body (first 100 chars): {data.content.body[:100]}")
print(f"data.content.footer: {data.content.footer}")

# # Alternate license
# data = client.get_sanctioned_content(
#     url="https://pioneervalleygazette.com/daydream",
#     max_price_micros=11000000,
#     currency="USD",
#     license_type=licenses.types.CUSTOM_LICENSE
#     license_id="<LICENSE_ID>"
# )
