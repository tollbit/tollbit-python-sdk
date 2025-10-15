from tollbit._apis.models import (
    ContentRate,
    RatePrice,
    RateLicenseResponse,
    DeveloperContentResponseSuccess,
)
from tollbit._apis.models._hand_rolled.get_content import (
    DeveloperContent,
    DeveloperRateResponse,
    DeveloperContentResponseMetadata,
    RatePriceResponse,
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
    return DeveloperContentResponseSuccess(
        metadata=DeveloperContentResponseMetadata(
            title="Sample Title",
            description="Sample Description",
            imageUrl="https://example.com/image.png",
            author="Author Name",
            published="2024-01-01T00:00:00Z",
            modified="2024-01-02T00:00:00Z",
        ),
        content=DeveloperContent(
            header="<header>Header Content</header>",
            main="<main>Main Content</main>",
            footer="<footer>Footer Content</footer>",
        ),
        rate=DeveloperRateResponse(
            price=RatePriceResponse(priceMicros=0, currency="USD"),
            license={
                "cuid": "license-cuid",
                "licenseType": "STANDARD",
                "licensePath": "/licenses/standard",
                "permissions": [],
                "validUntil": "2024-12-31T23:59:59Z",
            },
            error="",
        ),
    )
