from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Oferta:
    hurtownia: str
    EAN: str | None
    nazwa: str
    cena_netto: Decimal
    cena_brutto: Decimal
    url: str
