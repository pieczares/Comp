import os
from decimal import Decimal

import requests
from requests.adapters import HTTPAdapter

from models.Produkt import Produkt
from models.Oferta import Oferta

BASE_URL = os.environ.get("COMP_API_URL", "http://127.0.0.1:8000")

# Jedna sesja = ponowne użycie połączeń (loadery wysyłają wiele zapytań równolegle).
_SESSION = requests.Session()
_SESSION.mount("http://", HTTPAdapter(pool_maxsize=16))
_SESSION.mount("https://", HTTPAdapter(pool_maxsize=16))


class BladApi(Exception):
    """Problem z komunikacją z serwerem. Komunikat nadaje się do pokazania użytkownikowi."""


class ProduktApi:

    @staticmethod
    def _pobierz_json(sciezka: str, params: dict | None = None):
        params = {k: v for k, v in (params or {}).items() if v is not None}
        try:
            response = _SESSION.get(
                f"{BASE_URL}{sciezka}",
                params=params,
                headers={"Accept": "application/json"},
                timeout=(10, 30),
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as e:
            raise BladApi("Serwer nie odpowiada (przekroczono limit czasu).") from e
        except requests.exceptions.ConnectionError as e:
            raise BladApi(
                "Nie można połączyć się z serwerem. Sprawdź, czy jest uruchomiony."
            ) from e
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            raise BladApi(f"Serwer zwrócił błąd (kod {status}).") from e
        except ValueError as e:
            raise BladApi("Serwer zwrócił nieprawidłową odpowiedź.") from e
        except requests.exceptions.RequestException as e:
            raise BladApi(f"Błąd komunikacji z serwerem: {e}") from e

    @staticmethod
    def _oferta_z_dict(dane: dict) -> Oferta:
        jednostka = dane["jednostka"]
        if jednostka not in {"szt", "kg"}:
            raise ValueError(f"Nieprawidłowa jednostka: {jednostka!r}")

        return Oferta(
            hurtownia=str(dane["hurtownia"]),
            cena_netto=Decimal(str(dane["cena_netto"])),
            cena_brutto=Decimal(str(dane["cena_brutto"])),
            jednostka=jednostka,
        )

    def pobierz_oferty_api(self, hurtownia_id=None, kod=None) -> list[Oferta]:
        dane = self._pobierz_json(
            "/produkty/oferta", {"hurtownia_id": hurtownia_id, "kod": kod}
        )

        if not isinstance(dane, list):
            raise BladApi("Serwer powinien zwrócić listę ofert.")

        try:
            return [self._oferta_z_dict(produkt) for produkt in dane]
        except (KeyError, TypeError, ValueError, ArithmeticError) as e:
            raise BladApi(f"Serwer zwrócił nieprawidłowe dane ofert: {e}") from e

    def pobierz_cene_api(self, hurtownia: str, kod: str) -> Oferta:
        dane = self._pobierz_json(
            "/produkty/cena", {"hurtownia": hurtownia, "kod": kod}
        )

        if not isinstance(dane, dict):
            raise BladApi("Serwer powinien zwrócić obiekt z ceną.")

        try:
            return self._oferta_z_dict(dane)
        except (KeyError, TypeError, ValueError, ArithmeticError) as e:
            raise BladApi(f"Serwer zwrócił nieprawidłowe dane ceny: {e}") from e

    def pobierz_produkty_api(self, kod=None, limit=None, offset=None) -> list[Produkt]:
        dane = self._pobierz_json(
            "/produkty", {"kod": kod, "limit": limit, "offset": offset}
        )

        if not isinstance(dane, list):
            raise BladApi("Serwer powinien zwrócić listę produktów.")

        produkty: list[Produkt] = []

        try:
            for item in dane:
                produkty.append(Produkt(name=str(item["nazwa"]), EAN=str(item["kod"])))
        except (KeyError, TypeError) as e:
            raise BladApi(f"Serwer zwrócił nieprawidłowe dane produktów: {e}") from e

        return produkty

    def pobierz_produkty_count_api(self) -> int:
        dane = self._pobierz_json("/produkty/count")

        if not isinstance(dane, dict) or "count" not in dane:
            raise BladApi("Serwer powinien zwrócić pole 'count'.")

        try:
            return int(dane["count"])
        except (TypeError, ValueError) as e:
            raise BladApi("Serwer zwrócił nieprawidłową liczbę produktów.") from e
