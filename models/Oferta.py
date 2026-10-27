from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass
class Oferta:
    hurtownia: str
    cena_netto: Decimal
    cena_brutto: Decimal
    jednostka: Literal["szt","kg"]
