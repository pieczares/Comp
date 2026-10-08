from dataclasses import dataclass

@dataclass
class Product:
    name: str
    category: str
    symbol: str
    offers: list[tuple[str, float]]

    @property
    def lowest_price(self) -> float:
        return min(price for _, price in self.offers)