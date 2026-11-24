from integrations.Produkt_api import ProduktApi
from ui.Worker import Worker


class ProductsLoader(Worker):
    """Wątek OffersPage: pobiera jedną stronę produktów.

    Jeśli liczba wszystkich produktów nie jest jeszcze znana, pobiera ją też.
    Wynik (`done`): krotka (liczba_produktów, lista_produktów).
    """

    def __init__(self, token: int, limit, offset: int, liczba_produktow: int | None = None, parent=None):
        super().__init__(token, parent)
        self._limit = limit
        self._offset = offset
        self._liczba_produktow = liczba_produktow

    def zadanie(self):
        api = ProduktApi()
        liczba = self._liczba_produktow
        if liczba is None:
            liczba = api.pobierz_produkty_count_api()
        produkty = api.pobierz_produkty_api(limit=self._limit, offset=self._offset)
        return liczba, produkty
