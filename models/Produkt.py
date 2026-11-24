from models.Oferta import Oferta

class Produkt:

    def __init__(self, name: str, EAN: str, offers: list[Oferta]):
        self.name = name
        self.EAN = EAN
        self.offers = offers
        self.offers = self.get_offers()

    def get_offers(self)-> list[Oferta]:
        #import jest tutaj aby uniknąć pętli czy coś takiego
        from integrations.Produkt_api import ProduktApi
        return ProduktApi().pobierz_oferty_api(kod=self.EAN)

    def lowest_price(self) -> Oferta | None:
        return min(
            self.offers,
            key=lambda oferta: oferta.cena_brutto,
            default=None,
        )
