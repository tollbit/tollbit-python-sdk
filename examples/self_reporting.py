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

daydream_rate_info = client.get_rate(url="https://pioneervalleygazette.com/daydream")
daydream_license = daydream_rate_info[0].license

sunset_rate_info = client.get_rate(url="https://pioneervalleygazette.com/sunset")
sunset_license = sunset_rate_info[0].license

print("Daydream rate info:", daydream_rate_info[0].model_dump())
print("Sunset rate info:", sunset_rate_info[0].model_dump())

reporting_client = self_reporting.create_client(secret_key=api_key, user_agent=user_agent)

usages = []
usages.append(
    self_reporting.usage(
        url="https://pioneervalleygazette.com/daydream",
        times_used=1,
        license_permissions=[licences.LICENSE_PERMISSION_PARTIAL_USE],
        license_cuid=daydream_license.cuid,
        license_type=licences.ON_DEMAND_LICENSE,
    )
)

usages.append(
    self_reporting.usage(
        url="https://pioneervalleygazette.com/sunset",
        times_used=2,
        license_permissions=[licences.LICENSE_PERMISSION_PARTIAL_USE],
        license_cuid=sunset_license.cuid,
        license_type=licences.ON_DEMAND_FULL_USE_LICENSE,
        metadata={"another_key": "another_value"},
    )
)

# We create a transaction here that is idempotent, so that every
# reporting request can be safely multiple times.
tb = reporting_client.create_transaction_block(usages)
result = reporting_client.report(tb)


print("Transaction result:", [r.model_dump() for r in result])
