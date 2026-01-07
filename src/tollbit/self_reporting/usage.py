from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from tollbit.licenses.types import LicenseType
from tollbit.licenses.permissions import LicensePermission


def usage(
    url: str,
    times_used: int,
    license_permissions: list[LicensePermission],
    license_id: str,
    license_type: LicenseType,
    metadata: dict[str, Any] | None = None,
) -> Usage:
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
    license_id: str
    license_type: LicenseType
    metadata: dict[str, Any] | None = None
