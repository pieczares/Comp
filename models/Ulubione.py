from models.Produkt import Produkt


class Ulubione:

    produkty: list[Produkt]

    def __init__(self):
        self.produkty = []

    def check_if_product_exists(self, EAN: str) -> int:
        for index, item in enumerate(self.produkty):
            if item.EAN == EAN:
                return index
        return -1

    def dodaj_produkt(self, produkt: Produkt):
        if self.check_if_product_exists(produkt.EAN) != -1:
            return
        self.produkty.append(produkt)

    def usun_produkt(self, produkt: Produkt):
        index = self.check_if_product_exists(produkt.EAN)
        if index != -1:
            del self.produkty[index]
