from decimal import Decimal

import requests

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
        raise ValueError("API powinno zwrócić listę produktów.")

    oferty: list[Oferta] = []

    for produkt in dane:
        jednostka = produkt["jednostka"]

        if jednostka not in {"szt", "kg"}:
            raise ValueError(
                f"Nieprawidłowa jednostka: {jednostka!r}"
            )

        oferta = Oferta(
            hurtownia_id=int(produkt["hurtownia_id"]),
            kod=str(produkt["kod"]),
            cena_netto=Decimal(str(produkt["netto"])),
            cena_brutto=Decimal(str(produkt["brutto"])),
            jednostka=jednostka,
        )

        oferty.append(oferta)

    return oferty