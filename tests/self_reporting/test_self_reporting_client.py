import pytest
from tollbit._apis.self_reporting_api import SelfReportingAPI
from tollbit.self_reporting.client import SelfReportingClient, TransactionBlock
from tollbit.self_reporting.usage import usage
from tollbit import licences
from tollbit._apis.models import (
    SelfReportContentUsageRequest,
    SelfReportContentUsageResponse,
    SelfReportUsageReceipt,
)
from unittest.mock import MagicMock


def test_self_report_usage():
    mock_self_reporting_api = MagicMock(spec=SelfReportingAPI)
    mock_self_reporting_api.post_self_report.return_value = SelfReportContentUsageResponse(
        receipts=[
            SelfReportUsageReceipt(
                url="https://example.com/resource",
                perUnitPriceMicros=1000,
                totalUsePriceMicros=5000,
                currency="USD",
                license={
                    "id": "license-cuid-123",
                    "licenseType": "standard",
                    "licensePath": "/licenses/standard",
                    "permissions": [{"name": "PARTIAL_USE"}],
                },
            )
        ]
    )

    client = SelfReportingClient(self_reporting_api=mock_self_reporting_api)

    u = usage(
        url="https://example.com/resource",
        times_used=5,
        license_permissions=[licences.permissions.LICENSE_PERMISSION_FULL_USE],
        license_id="cuid_123",
        license_type=licences.types.ON_DEMAND_LICENSE,
    )
    tb = client.create_transaction_block([u])
    assert tb.idempotency_id is not None
    assert len(tb.usages) == 1

    result = client.report(tb)
    assert isinstance(result, SelfReportContentUsageResponse)

    mock_self_reporting_api.post_self_report.assert_called_once()
    call_args = mock_self_reporting_api.post_self_report.call_args[0][0]
    assert isinstance(call_args, SelfReportContentUsageRequest)
