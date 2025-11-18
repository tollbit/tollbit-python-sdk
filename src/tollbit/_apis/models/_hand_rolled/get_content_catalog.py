from __future__ import annotations
from pydantic import AnyUrl, BaseModel, Field, field_validator
from datetime import datetime
from typing import Any

# This supports older versions of python which do not correctly parse ISO 8601 datetime strings
from dateutil.parser import isoparse


class DeveloperContentCatalogResponse(BaseModel):
    contents: list[DeveloperContentCatalogPage]
    next_page_token: str | None = Field(
        serialization_alias="pageToken", validation_alias="pageToken"
    )


class DeveloperContentCatalogPage(BaseModel):
    property_id: str = Field(serialization_alias="propertyId", validation_alias="propertyId")
    page_url: str = Field(serialization_alias="pageUrl", validation_alias="pageUrl")
    last_mod: datetime | None = Field(serialization_alias="lastMod", validation_alias="lastMod")

    @field_validator("last_mod", mode="before")
    @classmethod
    def parse_last_mod(cls: type[DeveloperContentCatalogPage], v: str | None) -> datetime | None:
        if v is None:
            return v
        return isoparse(v)
