from models.Oferta import Oferta

class Produkt:

    def __init__(self, name: str, EAN: str):
        self.name = name
        self.EAN = EAN
        self.offers = self.get_offers()

    def get_offers(self)-> list[Oferta]:
        #import jest tutaj aby uniknąć pętli czy coś takiego
        from integrations.Produkt_api import ProduktApi
        try:
            return ProduktApi().pobierz_oferty_api(kod=self.EAN)
        except Exception as e:
            print(f"Nie udało się pobrać ofert dla produktu {self.EAN}: {e}")
            return []

    def lowest_price(self) -> Oferta | None:
        return min(
            self.offers,
            key=lambda oferta: oferta.cena_brutto,
            default=None,
        )
