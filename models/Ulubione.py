from models.Produkt import Produkt


class Ulubione:

    produkty: list[Produkt]

    def __init__(self):
        self.produkty = []


    def dodaj_produkt(self, produkt: Produkt):
        self.produkty.append(produkt)

    def usun_produkt(self, produkt: Produkt):
        self.produkty.remove(produkt)