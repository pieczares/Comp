from dataclasses import dataclass

from models.Produkt import Produkt

@dataclass
class Koszyk:
    __oferty: list[tuple[Produkt, int]]

    def dodaj_oferte(self, oferta: Produkt, ilosc: int):
        for index, (produkt, i) in enumerate(self.__oferty):
            if produkt.EAN == oferta.EAN:
                self.__oferty[index] = (produkt, i+ilosc)
                return

        self.__oferty.append((oferta, ilosc))

    def usun_oferte(self, produkt: Produkt):
        self.__oferty = [
            (p, i)
            for p, i in self.__oferty
            if p.EAN != produkt.EAN
        ]

    def get_oferty(self) -> list[tuple[Produkt, int]]:
        return self.__oferty