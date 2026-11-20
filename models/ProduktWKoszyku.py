from dataclasses import dataclass
from decimal import Decimal

from integrations.Produkt_api import ProduktApi


@dataclass
class ProduktWKoszyku:
    EAN: str
    hurtownia: str
    ilosc: int
    cena_netto: Decimal = Decimal("0.00")
    cena_brutto: Decimal = Decimal("0.00")
    jednostka: str = ""
    nazwa: str = ""

    def pobierz_ceny (self):
        ceny = ProduktApi().pobierz_cene_api(self.hurtownia, self.EAN)
        self.cena_netto = ceny.cena_netto
        self.cena_brutto = ceny.cena_brutto
        self.jednostka = ceny.jednostka