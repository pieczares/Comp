from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PozycjaListy:
    kod: str
    nazwa: str
    cena_netto: Decimal
    cena_brutto: Decimal
    ilosc: int
    jednostka: str