# In this example, we use self-reporting to report a usage of a page. This would occur
# when your own code accesses a page directly (not through the tollbit sudomain or via the SDK),
# and you want to report that usage to Tollbit for billing purposes.

from tollbit import self_reporting
from tollbit.self_reporting import Usage, TransactionBlock, AsyncSelfReportingClient
from tollbit import licenses
from tollbit import use_content
import os
from dataclasses import dataclass
from anyio import create_memory_object_stream, create_task_group, run
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream

# Replace with your actual organization API key or set it as an environment variable
api_key = os.getenv("TOLLBIT_ORG_API_KEY", "YOUR_API_KEY_HERE")
user_agent = os.getenv("TOLLBIT_USER_AGENT", "tollbit-python-sdk-example/0.1.0")


@dataclass
class Rates:
    url: str
    rate_info: any


def print_rate(rates: Rates):
    print(f"RATE {rates.url}:")
    for ix, rate in enumerate(rates.rate_info):
        print("Rate index", ix)
        print(f"rate.price.price_micros: {rate.price.price_micros}")
        print(f"rate.price.currency: {rate.price.currency}")
        print(f"rate.license.id: {rate.license.id}")
        print(f"rate.license.license_type: {rate.license.license_type}")
        print(f"rate.license.license_path: {rate.license.license_path}")
        print(f"rate.permissions: {rate.license.permissions}")


# When reporting usage, we need to create a transaction block that contains one or more usages. Transaction
# blocks are idenmpotent, meaning that if the same transaction block is reported multiple times, it will only be
# counted once for billing purposes. This is useful in case of network errors or other issues that might cause
# a report to be sent multiple times. Here we batch multiple usages into a single transaction block for efficiency.
async def batch_reporting_usages(
    client: AsyncSelfReportingClient,
    receive_usage: MemoryObjectReceiveStream[Usage],
    send_transaction: MemoryObjectSendStream[TransactionBlock],
):
    async with receive_usage:
        usages = []
        async for usage in receive_usage:
            usages.append(usage)
            if len(usages) >= 2:
                transaction_block = client.create_transaction_block(usages)
                await send_transaction.send(transaction_block)
                usages = []
        if len(usages) > 0:
            transaction_block = client.create_transaction_block(usages)
            await send_transaction.send(transaction_block)

    await send_transaction.aclose()


# Here we send the action transaction blocks to Tollbit for reporting and record the receipts.
async def report_transactions(
    client: AsyncSelfReportingClient,
    receive_transaction: MemoryObjectReceiveStream[TransactionBlock],
):
    async with receive_transaction:
        async for transaction_block in receive_transaction:
            result = await client.report(transaction_block)
            print("================================")
            print("Reporting Result:")
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


async def record_usage(send_usage: MemoryObjectSendStream[Usage], usage: Usage):
    async with send_usage:
        await send_usage.send(usage)


async def main():
    reporting_client = self_reporting.create_async_client(secret_key=api_key, user_agent=user_agent)
    send_usage, receive_usage = create_memory_object_stream[Usage]()
    send_transaction, receive_transaction = create_memory_object_stream[
        self_reporting.TransactionBlock
    ]()

    async with create_task_group() as tg:
        # Here's our pipeline for reporting usages
        tg.start_soon(report_transactions, reporting_client, receive_transaction)
        tg.start_soon(batch_reporting_usages, reporting_client, receive_usage, send_transaction)

        # Now we record some usages
        tg.start_soon(
            record_usage,
            send_usage.clone(),
            self_reporting.usage(
                url="https://pioneervalleygazette.com/daydream",
                times_used=1,
                license_permissions=[licenses.permissions.LICENSE_PERMISSION_PARTIAL_USE],
                license_type=licenses.types.ON_DEMAND_LICENSE,
            ),
        )
        tg.start_soon(
            record_usage,
            send_usage.clone(),
            self_reporting.usage(
                url="https://pioneervalleygazette.com/sunset",
                times_used=20,
                license_permissions=[licenses.permissions.LICENSE_PERMISSION_PARTIAL_USE],
                license_type=licenses.types.ON_DEMAND_LICENSE,
            ),
        )
        tg.start_soon(
            record_usage,
            send_usage.clone(),
            self_reporting.usage(
                url="https://pioneervalleygazette.com/frog",
                times_used=5,
                license_permissions=[licenses.permissions.LICENSE_PERMISSION_PARTIAL_USE],
                license_type=licenses.types.ON_DEMAND_LICENSE,
            ),
        )

        await send_usage.aclose()


run(main)
