# In this example, we use self-reporting to report a usage of a page. This would occur 
# when your own code accesses a page directly (not through the tollbit sudomain or via the SDK),
# and you want to report that usage to Tollbit for billing purposes.

# DRAFTING API ONLY - WILL NOT RUN YET

from tollbit import self_reporting
from tollbit import licences
import os

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")


reporting_client = self_reporting.create_client(secret_key=api_key, user_agent=user_agent)

block = self_reporting.create_transaction_block()
block.add_usage(
    url="https://pioneervalleygazette.com/daydream",
    times_used=1,
    license_permissions=[licences.permission.LICENSE_PERMISSION_PARTIAL_USE],
    license_cuid="license-cuid-example-1234",
    license_type=licences.ON_DEMAND_LICENSE,
)
block.add_usage(
    url="https://pioneervalleygazette.com/sunset",
    times_used=2,
    license_permissions=[licenses.permission.LICENSE_PERMISSION_FULL_USE, licenses.permission.LICENSE_PERMISSION_CITATION_REQURED],
    license_cuid="license-cuid-example-5678",
    license_type=licences.type.ON_DEMAND_FULL_USE_LICENSE,
    metadata={"another_key": "another_value"},
)

result = reporting_client.submit_transaction_block(block)

print("Transaction result:", result)