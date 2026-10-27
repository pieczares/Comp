from decimal import Decimal

import requests

from models.Product import Product
from models.Oferta import Oferta


def pobierz_oferty_api(url: str) -> list[Oferta]:
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

def pobierz_produkty_api(url: str) ->list[Product]:
    response = requests.get(
        url,
        headers={"Accept": "application/json"},
        timeout=(10, 30),
    )
    response.raise_for_status()

    dane = response.json()

    if not isinstance(dane, list):
        raise ValueError("API powinno zwrócić listę produktów.")

    produkty: list[Product] = []

    for item in dane:
        produkt = Product(
            name=str(item["nazwa"]),
            EAN=str(item["kod"]),
            offers=[],
        )

        produkty.append(produkt)

    return produkty