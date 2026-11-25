from models.Oferta import Oferta


class Produkt:
    """Produkt z listą ofert. Model nie wykonuje żadnych zapytań sieciowych.

    Oferty ładuje OffersLoader i zapisuje je przez `set_offers()` / `set_offers_error()`.
    Flagi `offers_loaded` i `offers_error` mają wartości domyślne na poziomie klasy
    (zgodność ze starymi plikami .pkl) i nie są zapisywane do pliku.
    """

    offers_loaded: bool = False
    offers_error: str | None = None

    def __init__(self, name: str, EAN: str):
        self.name = name
        self.EAN = EAN
        self.offers: list[Oferta] = []

    def set_offers(self, offers: list[Oferta]):
        self.offers = list(offers)
        self.offers_loaded = True
        self.offers_error = None

    def set_offers_error(self, message: str):
        self.offers_loaded = False
        self.offers_error = message

    def __getstate__(self):
        stan = self.__dict__.copy()
        stan.pop("offers_loaded", None)
        stan.pop("offers_error", None)
        return stan

    def lowest_price(self) -> Oferta | None:
        return min(
            self.offers,
            key=lambda oferta: oferta.cena_brutto,
            default=None,
        )
