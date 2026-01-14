# In this example, we use self-reporting to report a usage of a page. This would occur
# when your own code accesses a page directly (not through the tollbit sudomain or via the SDK),
# and you want to report that usage to Tollbit for billing purposes.

from tollbit import self_reporting
from tollbit import licenses
from tollbit import use_content
import os

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")

reporting_client = self_reporting.create_client(secret_key=api_key, user_agent=user_agent)

# When reporting usage, we need to create a transaction block that contains one or more usages. Transaction
# blocks are idenmpotent, meaning that if the same transaction block is reported multiple times, it will only be
# counted once for billing purposes. This is useful in case of network errors or other issues that might cause
# a report to be sent multiple times.
usages = []
usages.append(
    # This usage represents accessing a page with one of our standard licenses (ON_DEMAND_LICENSE, ON_DEMAND_FULL_USE_LICENSE).
    # We don't need to provide a license_id in this case, as Tollbit will handle that for us.
    self_reporting.usage(
        url="https://pioneervalleygazette.com/daydream",
        times_used=1,
        license_permissions=[licenses.permissions.LICENSE_PERMISSION_PARTIAL_USE],
        license_type=licenses.types.ON_DEMAND_LICENSE,
    )
)

transaction_block = reporting_client.create_transaction_block(usages)

# Now we can report the transaction block to Tollbit
result = reporting_client.report(transaction_block)
print("Receipts:")
for ix, receipt in enumerate(result.receipts):
    print("Receipt index", ix)
    print(f"receipt.url: {receipt.url}")
    print(f"receipt.per_unit_price_micros: {receipt.per_unit_price_micros}")
    print(f"receipt.total_use_price_micros: {receipt.total_use_price_micros}")
    print(f"receipt.currency: {receipt.currency}")
    print(f"receipt.license.id: {receipt.license.id}")
    print(f"receipt.license.license_type: {receipt.license.license_type}")
    print(f"receipt.license.license_path: {receipt.license.license_path}")
    print(f"receipt.license.permissions: {receipt.license.permissions}")
