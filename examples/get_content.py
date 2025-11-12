# In this example, we demonstrate how to use the Tollbit Python SDK 
# to get content rate information for a specific URL.
from tollbit import use_content
from tollbit import licences
from tollbit import currencies
from tollbit import content_formats
from tollbit import use_content
import os

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")

client = use_content.create_client(
    secret_key=api_key, 
    user_agent=user_agent
)


data = client.get_sanctioned_content(
    url="https://pioneervalleygazette.com/daydream",
    max_price_micros=11000000,
    currency=currencies.USD,
    license_type=licences.ON_DEMAND_LICENSE
)
print("Markdown data:", data)

data = client.get_sanctioned_content(
    url="https://pioneervalleygazette.com/daydream",
    max_price_micros=11000000,
    currency=currencies.USD,
    license_type=licences.ON_DEMAND_LICENSE,
    format=content_formats.html
)
print("HTML data:", data)

# # Alternate license
# data = client.get_sanctioned_content(
#     url="https://pioneervalleygazette.com/daydream",
#     max_price_micros=11000000,
#     currency="USD",
#     license_type=licences.CUSTOM_LICENSE
#     license_id="<LICENSE_ID>"
# )