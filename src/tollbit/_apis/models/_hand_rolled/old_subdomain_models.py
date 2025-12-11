from __future__ import annotations
from datetime import datetime
from typing import Any, List
from pydantic import BaseModel


class RatePrice(BaseModel):
    priceMicros: int
    currency: str


class ContentRate(BaseModel):
    price: RatePrice
    license: RateLicenseResponse
    error: str


class RateLicenseResponse(BaseModel):
    cuid: str | None
    licenseType: str
    licensePath: str
    permissions: List[RateLicensePermission]


class RateLicensePermission(BaseModel):
    name: str
