# In this example, we demonstrate how to use the Tollbit Python SDK
# to get content rate information for a specific URL.
from tollbit import use_content
from tollbit import crawl_content
import os

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")

client = use_content.create_client(secret_key=api_key, user_agent=user_agent)
rate_info = client.get_rate(url="https://pioneervalleygazette.com/daydream")

# rate_info is a list of ContentRate objects, which is a Pydantic model.
# We can print out the details.

print(f"{len(rate_info)} Content Rates:")
for rate in rate_info:
    print("Content Rate:")
    print(f"  Price (micros): {rate.price.price_micros}")
    print(f"  Currency: {rate.price.currency}")
    print(f"  License ID: {rate.license.id}")
    print(f"  License Type: {rate.license.license_type}")
    print(f"  License Path: {rate.license.license_path}")
    print(f"  Permissions: {rate.license.permissions}")

# We can also get the rates using the crawl client
crawl = crawl_content.create_client(secret_key=api_key, user_agent=user_agent)
crawl_rate_info = crawl.get_rate(url="https://pioneervalleygazette.com/daydream")

print(f"{len(rate_info)} Content Rates:")
for rate in rate_info:
    print("Content Rate:")
    print(f"  Price (micros): {rate.price.price_micros}")
    print(f"  Currency: {rate.price.currency}")
    print(f"  License ID: {rate.license.id}")
    print(f"  License Type: {rate.license.license_type}")
    print(f"  License Path: {rate.license.license_path}")
    print(f"  Permissions: {rate.license.permissions}")
