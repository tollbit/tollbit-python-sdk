from urllib.parse import urlparse, ParseResult


def parse_url_with_forgiveness(url: str) -> ParseResult:
    """Parse a URL, adding 'https://' if no scheme is present."""
    if not urlparse(url).scheme:
        url_to_parse = f"https://{url}"
    else:
        url_to_parse = url
    return urlparse(url_to_parse)


def content_urls(url: str) -> tuple[str, str]:
    """Return matching token and retrieval URLs, preserving queries and path parameters.

    Fragments are client-side only. Query parameters, including unknown or signed
    parameters, must remain identical in the token and the content request.
    """
    parsed = parse_url_with_forgiveness(url)._replace(fragment="")
    return parsed.geturl(), parsed._replace(scheme="").geturl().removeprefix("//")
