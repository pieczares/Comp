from integrations.Produkt_api import ProduktApi
from ui.Worker import Worker


class PricesLoader(Worker):
    """Wątek koszyka: pobiera aktualne ceny dla listy (hurtownia, EAN).

    Pierwszy błąd przerywa całość (unikamy wielu timeoutów z rzędu).
    Wynik (`done`): lista Oferta w tej samej kolejności co `klucze`.
    """

    def __init__(self, token: int, klucze: list[tuple[str, str]], parent=None):
        super().__init__(token, parent)
        self._klucze = list(klucze)

    def zadanie(self):
        api = ProduktApi()
        return [api.pobierz_cene_api(hurtownia, ean) for hurtownia, ean in self._klucze]
