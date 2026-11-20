from decimal import Decimal
from urllib.parse import urlencode

import requests

from models.Produkt import Produkt
from models.Oferta import Oferta

class ProduktApi:


    def pobierz_oferty_api(self, hurtownia_id=None, kod=None) -> list[Oferta]:

        url = f"http://127.0.0.1:8000/produkty/oferta"
        params = {"hurtownia_id": hurtownia_id, "kod": kod}
        params = {k: v for k, v in params.items() if v is not None}
        url = f"{url}?{urlencode(params)}" if params else url

        response = requests.get(
            url,
            headers={"Accept": "application/json"},
            timeout=(10, 30),
        )
        response.raise_for_status()

        dane = response.json()

        if not isinstance(dane, list):
            raise ValueError("API powinno zwrócić listę ofert.")

        oferty: list[Oferta] = []

        for produkt in dane:
            jednostka = produkt["jednostka"]

            if jednostka not in {"szt", "kg"}:
                raise ValueError(
                    f"Nieprawidłowa jednostka: {jednostka!r}"
                )

            oferta = Oferta(
                hurtownia=str(produkt["hurtownia"]),
                cena_netto=Decimal(str(produkt["cena_netto"])),
                cena_brutto=Decimal(str(produkt["cena_brutto"])),
                jednostka=jednostka,
            )

            oferty.append(oferta)

        return oferty

    def pobierz_cene_api(self, hurtownia: str, kod: str) -> Oferta:
        response = requests.get(
            "http://127.0.0.1:8000/produkty/cena",
            params={"hurtownia": hurtownia, "kod": kod},
            headers={"Accept": "application/json"},
            timeout=(10, 30),
        )
        response.raise_for_status()
        dane = response.json()

        if not isinstance(dane, dict):
            raise ValueError("API powinno zwrócić obiekt.")

        jednostka = dane["jednostka"]
        if jednostka not in {"szt", "kg"}:
            raise ValueError(f"Nieprawidłowa jednostka: {jednostka!r}")

        return Oferta(
            hurtownia=str(dane["hurtownia"]),
            cena_netto=Decimal(str(dane["cena_netto"])),
            cena_brutto=Decimal(str(dane["cena_brutto"])),
            jednostka=jednostka,
        )

    def pobierz_produkty_api(self, kod=None, limit=None, offset=None) ->list[Produkt]:

        url = "http://127.0.0.1:8000/produkty"

        params = {"kod": kod, "limit": limit, "offset": offset}
        params = {k: v for k, v in params.items() if v is not None}
        url = f"{url}?{urlencode(params)}" if params else url

        response = requests.get(
            url,
            headers={"Accept": "application/json"},
            timeout=(10, 30),
        )
        response.raise_for_status()

        dane = response.json()

        if not isinstance(dane, list):
            raise ValueError("API powinno zwrócić listę produktów.")

        produkty: list[Produkt] = []

        for item in dane:
            produkt = Produkt(
                name=str(item["nazwa"]),
                EAN=str(item["kod"]),
                offers=[],
            )

            produkty.append(produkt)

        return produkty

    def pobierz_produkty_count_api(self) -> int:
        response = requests.get(
            "http://127.0.0.1:8000/produkty/count",
            headers={"Accept": "application/json"},
            timeout=(10, 30),
        )
        response.raise_for_status()
        dane = response.json()
        if not isinstance(dane, dict):
            raise ValueError("API powinno zwrócić słownik.")
        if "count" not in dane:
            raise ValueError("API powinno zwrócić pole 'count'.")

        return int(dane["count"])
