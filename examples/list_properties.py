from tollbit import crawl_content
import os

api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")

client = crawl_content.create_client(secret_key=api_key, user_agent=user_agent)

properties = client.list_properties(page_size=5, ready_to_license=True)

for prop in properties.items:
    print(f"{prop.domain} ({prop.name}) added {prop.added_at}")
    for license in prop.licenses:
        print(f"  {license.type}: rates enabled={license.rates_enabled}")
        for rate in license.rates:
            print(f"    {rate.path_prefix} {rate.price_micros} {rate.currency}")

if properties.next_token:
    next_page = client.list_properties(
        page_size=5, page_token=properties.next_token, ready_to_license=True
    )
    print([prop.domain for prop in next_page.items])
