from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from tollbit.licenses.types import LicenseType, CUSTOM_LICENSE
from tollbit.licenses.permissions import LicensePermission


def usage(
    url: str,
    times_used: int,
    license_permissions: list[LicensePermission],
    license_type: LicenseType,
    license_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Usage:
    if license_type == CUSTOM_LICENSE and not license_id:
        raise ValueError("license_id must be provided for CUSTOM_LICENSE type")

    return Usage(
        url=url,
        times_used=times_used,
        license_permissions=license_permissions,
        license_id=license_id,
        license_type=license_type,
        metadata=metadata,
    )


@dataclass(frozen=True)
class Usage:
    url: str
    times_used: int
    license_permissions: list[LicensePermission]
    license_type: LicenseType
    license_id: str | None = None
    metadata: dict[str, Any] | None = None
