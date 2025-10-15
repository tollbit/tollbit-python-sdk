from typing import TypeAlias, NewType
from tollbit._apis.models import ContentRate as APIContentRate

ContentRate: TypeAlias = APIContentRate
ContentRates: TypeAlias = list[ContentRate]
