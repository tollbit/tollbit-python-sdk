from __future__ import annotations
from enum import Enum
from pydantic import AnyUrl, BaseModel, Field


class DeveloperContentResponseSuccess(BaseModel):
    content: DeveloperContent
    metadata: DeveloperContentResponseMetadata
    rate: DeveloperRateResponse


class DeveloperContentResponseMetadata(BaseModel):
    title: str | None
    description: str | None
    image_url: str | None = Field(serialization_alias="imageUrl", validation_alias="imageUrl")
    author: str | None
    published: str | None
    modified: str | None


class DeveloperContent(BaseModel):
    header: str
    main: str
    footer: str


class DeveloperRateResponse(BaseModel):
    price: RatePriceResponse
    license: RateLicenseResponse
    error: str


class RatePriceResponse(BaseModel):
    price_micros: int = Field(serialization_alias="priceMicros", validation_alias="priceMicros")
    currency: str


class RateLicenseResponse(BaseModel):
    cuid: str
    license_type: str = Field(serialization_alias="licenseType", validation_alias="licenseType")
    license_path: str = Field(serialization_alias="licensePath", validation_alias="licensePath")
    permissions: list[RateLicensePermission]
    valid_until: str = Field(serialization_alias="validUntil", validation_alias="validUntil")


class RateLicensePermission(BaseModel):
    name: str
