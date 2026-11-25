from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import Signal

from integrations.Produkt_api import BladApi, ProduktApi
from loaders.Worker import Worker


class OffersLoader(Worker):
    """Pobiera oferty dla listy EAN-ów (kilka zapytań równolegle).

    Dla każdego EAN-u emituje `item(token, ean, oferty, blad)`: `oferty` to lista Oferta
    albo None, gdy wystąpił błąd (wtedy `blad` zawiera komunikat). Dzięki temu karty
    uzupełniają się na bieżąco. Po 3 błędach z rzędu (bez żadnego sukcesu) reszta
    jest pomijana z tym samym komunikatem, żeby nie czekać na kolejne timeouty.
    """

    item = Signal(int, str, object, object)

    MAX_WATKOW = 6
    MAX_BLEDOW = 3

    def __init__(self, token: int, eany: list[str], parent=None):
        super().__init__(token, parent)
        self._eany = list(dict.fromkeys(eany))

    def zadanie(self):
        api = ProduktApi()
        stan = {"ok": 0, "blad": 0, "komunikat": ""}

        def pobierz(ean: str):
            if self.anulowano:
                return
            if stan["ok"] == 0 and stan["blad"] >= self.MAX_BLEDOW:
                oferty, blad = None, stan["komunikat"]
            else:
                try:
                    oferty, blad = api.pobierz_oferty_api(kod=ean), None
                    stan["ok"] += 1
                except BladApi as e:
                    oferty, blad = None, str(e)
                except Exception as e:
                    oferty, blad = None, f"Nieoczekiwany błąd: {e}"
                if blad is not None:
                    stan["blad"] += 1
                    stan["komunikat"] = blad
            if not self.anulowano:
                self._emit(self.item, self._token, ean, oferty, blad)

        with ThreadPoolExecutor(max_workers=self.MAX_WATKOW) as pool:
            list(pool.map(pobierz, self._eany))
        return None
