from enum import Enum


class Currency(str, Enum):
    USD = "USD"


USD = Currency.USD
