from urllib.parse import urlparse


def parse_url_with_forgiveness(url: str) -> urlparse:
    """Parse a URL, adding 'https://' if no scheme is present."""
    if not urlparse(url).scheme:
        url_to_parse = f"https://{url}"
    else:
        url_to_parse = url
    return urlparse(url_to_parse)
