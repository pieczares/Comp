from dataclasses import dataclass
from decimal import Decimal

from models.Produkt import Produkt

@dataclass
class Alarm:
    __produkt: Produkt
    __cena: Decimal
    __czy_aktywny: bool = True

    def zmien_cene(self, cena: Decimal):
        temp=self.__cena
        self.__cena = cena
        print("cena zmieniona z ", temp, "na ", cena)

    def zmien_aktywnosc(self):
        self.__czy_aktywny != self.__czy_aktywny
        if self.__czy_aktywny:
            print("włączony")
        else:
            print("wyłączony")
