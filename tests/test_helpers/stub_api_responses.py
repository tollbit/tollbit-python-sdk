from datetime import datetime
from dateutil.parser import parse
from tollbit._apis.models import (
    ContentRate,
    RatePrice,
    RateLicenseResponse,
    DeveloperContentCatalogResponse,
    GetContentResponse,
)


def stub_rate_response():
    return ContentRate(
        price=RatePrice(priceMicros=0, currency="USD"),
        license=RateLicenseResponse(
            licenseType="STANDARD",
            licensePath="/licenses/standard",
            permissions=[],
            validUntil="2024-12-31T23:59:59Z",
        ),
        error="",
    )


def stub_content_response():
    return GetContentResponse.model_validate(
        {
            "metadata": {
                "title": "Sample Title",
                "description": "Sample Description",
                "imageUrl": "https://example.com/image.png",
                "author": "Author Name",
                "published": "2024-01-01T00:00:00Z",
                "modified": "2024-01-02T00:00:00Z",
            },
            "content": {
                "header": "<header>Header Content</header>",
                "body": "<main>Main Content</main>",
                "footer": "<footer>Footer Content</footer>",
            },
            "rate": {
                "price": {"priceMicros": 0, "currency": "USD"},
                "license": {
                    "id": "license-cuid",
                    "licenseType": "STANDARD",
                    "licensePath": "/licenses/standard",
                    "permissions": [],
                    "validUntil": "2024-12-31T23:59:59Z",
                },
            },
        }
    )


def stub_crawl_response():
    return GetContentResponse.model_validate(
        {
            "metadata": {
                "title": "Sample Title",
                "description": "Sample Description",
                "imageUrl": "https://example.com/image.png",
                "author": "Author Name",
                "published": "2024-01-01T00:00:00Z",
                "modified": "2024-01-02T00:00:00Z",
            },
            "content": {
                "header": "<header>Header Content</header>",
                "body": "<main>Main Content</main>",
                "footer": "<footer>Footer Content</footer>",
            },
            "rate": None,
        }
    )


def stub_catalog_response():
    return DeveloperContentCatalogResponse.model_validate(
        {
            "pageToken": None,
            "contents": [
                {
                    "propertyId": "property-123",
                    "pageUrl": "https://example.com/content-1",
                    "lastMod": "2024-01-01T00:00:00Z",
                }
            ],
        }
    )
