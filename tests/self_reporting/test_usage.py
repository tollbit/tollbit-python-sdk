import pytest
from tollbit.self_reporting.usage import usage
from tollbit import licenses


def test_usage_standard_license():
    u = usage(
        url="https://example.com/resource",
        times_used=3,
        license_permissions=[licenses.permissions.LICENSE_PERMISSION_FULL_USE],
        license_type=licenses.types.ON_DEMAND_LICENSE,
        metadata={"key": "value"},
    )
    assert u is not None
    assert u.license_id is None

    u = usage(
        url="https://example.com/resource",
        times_used=3,
        license_permissions=[licenses.permissions.LICENSE_PERMISSION_FULL_USE],
        license_type=licenses.types.ON_DEMAND_LICENSE,
        license_id="standard-license-123",  # Can optionally provide license_id
        metadata={"key": "value"},
    )
    assert u is not None
    assert u.license_id == "standard-license-123"


def test_usage_custom_license():
    u = usage(
        url="https://example.com/resource",
        times_used=5,
        license_permissions=[licenses.permissions.LICENSE_PERMISSION_PARTIAL_USE],
        license_type=licenses.types.CUSTOM_LICENSE,
        license_id="custom-license-456",
        metadata=None,
    )
    assert u is not None

    with pytest.raises(ValueError):
        usage(
            url="https://example.com/resource",
            times_used=5,
            license_permissions=[licenses.permissions.LICENSE_PERMISSION_PARTIAL_USE],
            license_type=licenses.types.CUSTOM_LICENSE,
            metadata=None,
        )

    with pytest.raises(ValueError):
        usage(
            url="https://example.com/resource",
            times_used=5,
            license_permissions=[licenses.permissions.LICENSE_PERMISSION_PARTIAL_USE],
            license_type=licenses.types.CUSTOM_LICENSE,
            license_id=None,
            metadata=None,
        )
