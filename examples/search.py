# In this example, we demonstrate how to use the Tollbit Python SDK
# to search for content across the TollBit platform.
from tollbit import search
import os

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")

client = search.create_client(secret_key=api_key, user_agent=user_agent)

# Basic search example
results = client.search(q="DIY home projects for millenials")

print("Search Results:")
print(f"Found {len(results.items)} results")
print(f"Next token: {results.nextToken}")
print()

for i, item in enumerate(results.items, 1):
    print(f"Result {i}:")
    print(f"  Title: {item.title}")
    print(f"  URL: {item.url}")
    print(f"  Published: {item.published_date}")
    print(f"  Publisher: {item.publisher.name} ({item.publisher.domain})")
    print(f"  Discoverable: {item.availability.discoverable}")
    print(f"  Ready to license: {item.availability.ready_to_license}")
    print()

# Search with size limit
results_limited = client.search(q="python tutorial", size=5)
print(f"Limited search results: {len(results_limited.items)} results")
print()

# Search on specific properties (domains to boost in results)
results_properties = client.search(
    q="tutorial",
    size=10,
    properties=["example.com", "tutorial.com"],
)
print(f"Search on specific properties: {len(results_properties.items)} results")
print()

# Pagination example - get next page using next_token
if results.nextToken:
    next_page = client.search(
        q="DIY home projects for millenials",
        next_token=results.nextToken,
    )
    print(f"Next page results: {len(next_page.items)} results")
    print()
