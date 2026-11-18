from dataclasses import dataclass


@dataclass
class ProduktWKoszyku:
    EAN: str
    hurtownia: str
    ilosc: int