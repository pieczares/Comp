from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import Signal

from integrations.Produkt_api import BladApi, ProduktApi
from loaders.Worker import Worker


class PricesLoader(Worker):
    """Wątek koszyka: pobiera aktualne ceny dla listy (hurtownia, EAN) równolegle.

    Dla każdej pozycji emituje `item(token, hurtownia, ean, cena, blad)`: `cena` to Oferta
    albo None, gdy wystąpił błąd (wtedy `blad` zawiera komunikat). Błąd jednej pozycji nie
    kasuje cen pozostałych. Po 3 błędach (bez żadnego sukcesu) reszta jest pomijana z tym
    samym komunikatem, żeby nie czekać na kolejne timeouty.
    Po zakończeniu emitowane jest `done` (wynik: None).
    """

    item = Signal(int, str, str, object, object)

    MAX_WATKOW = 6
    MAX_BLEDOW = 3

    def __init__(self, token: int, klucze: list[tuple[str, str]], parent=None):
        super().__init__(token, parent)
        self._klucze = list(dict.fromkeys(klucze))

    def zadanie(self):
        api = ProduktApi()
        stan = {"ok": 0, "blad": 0, "komunikat": ""}

        def pobierz(klucz: tuple[str, str]):
            if self.anulowano:
                return
            hurtownia, ean = klucz
            if stan["ok"] == 0 and stan["blad"] >= self.MAX_BLEDOW:
                cena, blad = None, stan["komunikat"]
            else:
                try:
                    cena, blad = api.pobierz_cene_api(hurtownia, ean), None
                    stan["ok"] += 1
                except BladApi as e:
                    cena, blad = None, str(e)
                except Exception as e:
                    cena, blad = None, f"Nieoczekiwany błąd: {e}"
                if blad is not None:
                    stan["blad"] += 1
                    stan["komunikat"] = blad
            if not self.anulowano:
                self._emit(self.item, self._token, hurtownia, ean, cena, blad)

        with ThreadPoolExecutor(max_workers=self.MAX_WATKOW) as pool:
            list(pool.map(pobierz, self._klucze))
        return None
