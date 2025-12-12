from tollbit._apis.models import Format as APIFormat
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class FormatData:
    header_string: str


class Format(Enum):
    html = FormatData(
        header_string="text/html",
    )
    markdown = FormatData(
        header_string="text/markdown",
    )


MARKDOWN = Format.markdown
HTML = Format.html
