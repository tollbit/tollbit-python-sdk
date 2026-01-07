from __future__ import annotations
from tollbit._apis.self_reporting_api import SelfReportingAPI, AsyncSelfReportingAPI
from tollbit._apis.models import (
    SelfReportContentUsageRequest,
    SelfReportContentUsageResponse,
    SelfReportUsage,
    SelfReportLicensePermission,
)
from tollbit._environment import env_from_vars
from dataclasses import dataclass
import uuid
from .usage import Usage


def create_client(
    secret_key: str,
    user_agent: str,
) -> SelfReportingClient:
    env = env_from_vars()

    return SelfReportingClient(
        self_reporting_api=SelfReportingAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
        ),
    )


def create_async_client(
    secret_key: str,
    user_agent: str,
) -> AsyncSelfReportingClient:
    env = env_from_vars()
    return AsyncSelfReportingClient(
        self_reporting_api=AsyncSelfReportingAPI(
            api_key=secret_key,
            user_agent=user_agent,
            env=env,
        ),
    )


class AsyncSelfReportingClient:
    self_reporting_api: AsyncSelfReportingAPI

    def __init__(
        self,
        self_reporting_api: AsyncSelfReportingAPI,
    ):
        self.self_reporting_api = self_reporting_api

    def create_transaction_block(self, usages: list[Usage]) -> TransactionBlock:
        return TransactionBlock(str(uuid.uuid4()), usages)

    async def report(self, transaction_block: TransactionBlock) -> SelfReportContentUsageResponse:
        api_usages = []

        for usage in transaction_block.usages:
            perms = [SelfReportLicensePermission(name=lp.value) for lp in usage.license_permissions]

            api_usages.append(
                SelfReportUsage(
                    url=usage.url,  # type: ignore
                    timesUsed=usage.times_used,
                    licensePermissions=perms,
                    licenseId=usage.license_id,
                    licenseType=usage.license_type.value,
                    metadata=usage.metadata,
                )
            )

        request = SelfReportContentUsageRequest(
            idempotencyId=transaction_block.idempotency_id,
            usage=api_usages,
        )

        return await self.self_reporting_api.post_self_report(request)


class SelfReportingClient:
    self_reporting_api: SelfReportingAPI

    def __init__(
        self,
        self_reporting_api: SelfReportingAPI,
    ):
        self.self_reporting_api = self_reporting_api

    def create_transaction_block(self, usages: list[Usage]) -> TransactionBlock:
        return TransactionBlock(str(uuid.uuid4()), usages)

    def report(self, transaction_block: TransactionBlock) -> SelfReportContentUsageResponse:
        api_usages = []

        for usage in transaction_block.usages:
            perms = [SelfReportLicensePermission(name=lp.value) for lp in usage.license_permissions]

            api_usages.append(
                SelfReportUsage(
                    url=usage.url,  # type: ignore
                    timesUsed=usage.times_used,
                    licensePermissions=perms,
                    licenseId=usage.license_id,
                    licenseType=usage.license_type.value,
                    metadata=usage.metadata,
                )
            )

        request = SelfReportContentUsageRequest(
            idempotencyId=transaction_block.idempotency_id,
            usage=api_usages,
        )

        return self.self_reporting_api.post_self_report(request)


@dataclass(frozen=True)
class TransactionBlock:
    idempotency_id: str
    usages: list[Usage]
