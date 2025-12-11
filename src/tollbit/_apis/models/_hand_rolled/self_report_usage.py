from __future__ import annotations
from datetime import datetime
from typing import Any, List
from pydantic import AnyUrl, BaseModel, Field, field_validator, ConfigDict
from pydantic.alias_generators import to_camel
from .old_subdomain_models import RateLicenseResponse


class TollbitAPIModel(BaseModel):
    """Base class for all API models."""

    model_config = ConfigDict(
        validate_by_name=True, validate_by_alias=True, alias_generator=to_camel
    )


class DeveloperSelfReportRequest(TollbitAPIModel):
    idempotency_id: str
    usage: List[SelfReportUsage]


class SelfReportUsage(TollbitAPIModel):
    url: str
    times_used: int
    license_permissions: List[SelfReportLicensePermission]
    license_cuid: str
    license_type: str
    metadata: dict[str, Any] | None = None


class SelfReportLicensePermission(TollbitAPIModel):
    name: str


class DeveloperTransactionResponse(TollbitAPIModel):
    url: str
    per_unit_price_micros: int
    total_use_price_micros: int
    currency: str
    license: RateLicenseResponse
