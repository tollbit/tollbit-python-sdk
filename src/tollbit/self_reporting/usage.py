from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from tollbit.licences import LicensePermission, LicenceType


def usage(
    url: str,
    times_used: int,
    license_permissions: list[LicensePermission],
    license_cuid: str,
    license_type: LicenceType,
    metadata: dict[str, Any] | None = None,
) -> Usage:
    return Usage(
        url=url,
        times_used=times_used,
        license_permissions=license_permissions,
        license_cuid=license_cuid,
        license_type=license_type,
        metadata=metadata,
    )


@dataclass(frozen=True)
class Usage:
    url: str
    times_used: int
    license_permissions: list[LicensePermission]
    license_cuid: str
    license_type: LicenceType
    metadata: dict[str, Any] | None = None
