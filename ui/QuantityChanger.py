from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel

from models.Koszyk import Koszyk


class QuantityChanger(QWidget):
    def __init__(self, koszyk:Koszyk, EAN:str, hurtownia:str, nazwa:str = "", on_change=None):
        super().__init__()
        self.koszyk = koszyk
        self.EAN = EAN
        self.hurtownia = hurtownia
        self.nazwa = nazwa
        self.on_change = on_change

        cart_layout = QHBoxLayout(self)

        minus_button = QPushButton("-")
        minus_button.clicked.connect(lambda: self.change_quantity(-1, quantity_label))
        minus_button.setProperty("class", "QuantityButton")
        cart_layout.addWidget(minus_button)

        quantity_label = QLabel("0")
        cart_layout.addWidget(quantity_label)

        plus_button = QPushButton("+")
        plus_button.clicked.connect(lambda: self.change_quantity(1, quantity_label))
        plus_button.setProperty("class", "QuantityButton")
        cart_layout.addWidget(plus_button)

        index = self.koszyk.check_if_offer_exists(self.EAN, self.hurtownia)
        if index != -1:
            quantity_label.setText(str(self.koszyk.get_oferty()[index].ilosc))
        else:
            quantity_label.setText("0")

    def change_quantity(self, delta: int, quantity_label: QLabel):
        index = self.koszyk.check_if_offer_exists(self.EAN, self.hurtownia)
        quantity = 0
        if index != -1:
            quantity = self.koszyk.get_oferty()[index].ilosc
        new_quantity = quantity + delta

        if new_quantity < 0:
            return

        self.koszyk.dodaj_oferte(self.EAN, self.hurtownia, new_quantity, self.nazwa)
        quantity_label.setText(str(new_quantity))
        if self.on_change:
            self.on_change()
