from dataclasses import dataclass
from decimal import Decimal

from integrations.Produkt_api import ProduktApi


class ProduktWKoszyku:

    def __init__(self, EAN: str, hurtownia: str, ilosc: int, nazwa: str = ""):
        self.EAN = EAN
        self.hurtownia = hurtownia
        self.ilosc = ilosc
        self.nazwa = nazwa
        self.cena_netto = Decimal("0.00")
        self.cena_brutto = Decimal("0.00")
        self.jednostka = ""


    def pobierz_ceny (self):
        ceny = ProduktApi().pobierz_cene_api(self.hurtownia, self.EAN)
        self.cena_netto = ceny.cena_netto
        self.cena_brutto = ceny.cena_brutto
        self.jednostka = ceny.jednostka