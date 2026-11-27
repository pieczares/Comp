from decimal import Decimal

from models.Produkt import Produkt


class Alarm:
    def __init__(self, produkt: Produkt, cena: Decimal):
        self.produkt = produkt
        self.cena = cena
        self.aktywny = True

    def zmien_cene(self, cena: Decimal):
        self.cena = cena

    def zmien_aktywnosc(self):
        self.aktywny = not self.aktywny

    def czy_spelniony(self) -> bool:
        oferta = self.produkt.lowest_price()
        if oferta is None:
            return False
        return oferta.cena_brutto <= self.cena
