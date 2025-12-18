# In this example, we use self-reporting to report a usage of a page. This would occur
# when your own code accesses a page directly (not through the tollbit sudomain or via the SDK),
# and you want to report that usage to Tollbit for billing purposes.

from tollbit import self_reporting
from tollbit import licences
from tollbit import use_content
import os

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")

# Get licenses for use in the transaction
client = use_content.create_client(secret_key=api_key, user_agent=user_agent)


# In this example we use get_rate to fetch the license information for two different URLs, specifically
# the ids of the licenses that we will be reporting usage against. In a real-world scenario, you would
# likely store these license ids somewhere after an initial retrieval, rather than fetching them
# every time you want to report usage.
daydream_rate_info = client.get_rate(url="https://pioneervalleygazette.com/daydream")
daydream_license = daydream_rate_info[0].license
sunset_rate_info = client.get_rate(url="https://pioneervalleygazette.com/sunset")
sunset_license = sunset_rate_info[0].license

print("Daydream rate info:")
for ix, rate in enumerate(daydream_rate_info):
    print("Rate index", ix)
    print(f"rate.price.priceMicros: {rate.price.priceMicros}")
    print(f"rate.price.currency: {rate.price.currency}")
    print(f"rate.license.id: {rate.license.id}")
    print(f"rate.license.licenseType: {rate.license.licenseType}")
    print(f"rate.license.licensePath: {rate.license.licensePath}")
    print(f"rate.permissions: {rate.license.permissions}")


print("Sunset rate info:")
for ix, rate in enumerate(sunset_rate_info):
    print("Rate index", ix)
    print(f"rate.price.priceMicros: {rate.price.priceMicros}")
    print(f"rate.price.currency: {rate.price.currency}")
    print(f"rate.license.id: {rate.license.id}")
    print(f"rate.license.licenseType: {rate.license.licenseType}")
    print(f"rate.license.licensePath: {rate.license.licensePath}")
    print(f"rate.permissions: {rate.license.permissions}")

reporting_client = self_reporting.create_client(secret_key=api_key, user_agent=user_agent)

# When reporting usage, we need to create a transaction block that contains one or more usages. Transaction
# blocks are idenmpotent, meaning that if the same transaction block is reported multiple times, it will only be
# counted once for billing purposes. This is useful in case of network errors or other issues that might cause
# a report to be sent multiple times.
usages = []
usages.append(
    self_reporting.usage(
        url="https://pioneervalleygazette.com/daydream",
        times_used=1,
        license_permissions=[licences.permissions.LICENSE_PERMISSION_PARTIAL_USE],
        license_id=daydream_license.id,
        license_type=licences.types.ON_DEMAND_LICENSE,
    )
)
usages.append(
    self_reporting.usage(
        url="https://pioneervalleygazette.com/sunset",
        times_used=2,
        license_permissions=[licences.permissions.LICENSE_PERMISSION_PARTIAL_USE],
        license_id=sunset_license.id,
        license_type=licences.types.ON_DEMAND_FULL_USE_LICENSE,
        metadata={"another_key": "another_value"},
    )
)
transaction_block = reporting_client.create_transaction_block(usages)

# Now we can report the transaction block to Tollbit
result = reporting_client.report(transaction_block)
print("Receipts:")
for ix, receipt in enumerate(result.receipts):
    print("Receipt index", ix)
    print(f"receipt.url: {receipt.url}")
    print(f"receipt.perUnitPriceMicros: {receipt.perUnitPriceMicros}")
    print(f"receipt.totalUsePriceMicros: {receipt.totalUsePriceMicros}")
    print(f"receipt.currency: {receipt.currency}")
    print(f"receipt.license.id: {receipt.license.id}")
    print(f"receipt.license.licenseType: {receipt.license.licenseType}")
    print(f"receipt.license.licensePath: {receipt.license.licensePath}")
    print(f"receipt.license.permissions: {receipt.license.permissions}")
