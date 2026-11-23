from dataclasses import dataclass

from models.ProduktWKoszyku import ProduktWKoszyku


class Koszyk:
    __oferty: list[ProduktWKoszyku]

    def __init__(self, oferty=None):
        if oferty is None:
            oferty = []
        self.__oferty = oferty


    def check_if_offer_exists(self, EAN:str, hurtownia:str) -> int:
        for index, item in enumerate(iterable=self.__oferty, start=0):
            if item.EAN == EAN and item.hurtownia == hurtownia:
                return index
        return -1

    def dodaj_oferte(self, EAN:str, hurtownia:str, ilosc:int, nazwa:str = ""):
        index = self.check_if_offer_exists(EAN=EAN, hurtownia=hurtownia)
        if index != -1:
            if ilosc <= 0:
                del self.__oferty[index]
                return
            self.__oferty[index].ilosc = ilosc
            return

        self.__oferty.append(
            ProduktWKoszyku(EAN=EAN, hurtownia=hurtownia, ilosc=ilosc, nazwa=nazwa)
        )

    def usun_oferte(self, EAN:str, hurtownia:str):
        index = self.check_if_offer_exists(EAN=EAN, hurtownia=hurtownia)
        if index != -1:
            del self.__oferty[index]

    def get_oferty(self) -> list[ProduktWKoszyku]:
        return self.__oferty
