from dataclasses import dataclass

from models.Oferta import Oferta

@dataclass
class Produkt:
    name: str
    EAN: str
    offers: list[Oferta]

    def __post_init__(self):
        self.offers = self.__get_offers()

    def __get_offers(self)-> list[Oferta]:
        #import jest tutaj aby uniknąć pętli czy coś takiego
        from integrations.Produkt_api import ProduktApi
        return ProduktApi.pobierz_oferty_api(f"http://127.0.0.1:8000/produkty/oferta?kod={self.EAN}")

    def lowest_price(self) -> Oferta | None:
        return min(
            self.offers,
            key=lambda oferta: oferta.cena_brutto,
            default=None,
        )