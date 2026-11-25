from concurrent.futures import ThreadPoolExecutor

from integrations.Produkt_api import ProduktApi
from loaders.Worker import Worker


class PricesLoader(Worker):
    """Wątek koszyka: pobiera aktualne ceny dla listy (hurtownia, EAN) równolegle.

    Pierwszy błąd (w kolejności `klucze`) przerywa całość, a oczekujące zapytania są
    anulowane (unikamy wielu timeoutów z rzędu).
    Wynik (`done`): lista Oferta w tej samej kolejności co `klucze`.
    """

    MAX_WATKOW = 6

    def __init__(self, token: int, klucze: list[tuple[str, str]], parent=None):
        super().__init__(token, parent)
        self._klucze = list(klucze)

    def zadanie(self):
        api = ProduktApi()

        def pobierz(klucz: tuple[str, str]):
            if self.anulowano:
                return None
            hurtownia, ean = klucz
            return api.pobierz_cene_api(hurtownia, ean)

        pool = ThreadPoolExecutor(max_workers=self.MAX_WATKOW)
        try:
            return list(pool.map(pobierz, self._klucze))
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
