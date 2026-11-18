from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit

from models.Koszyk import Koszyk


class QuantityChanger(QWidget):
    def __init__(self, koszyk: Koszyk, EAN: str, hurtownia: str, nazwa: str = "", on_change=None):
        super().__init__()
        self.koszyk = koszyk
        self.EAN = EAN
        self.hurtownia = hurtownia
        self.nazwa = nazwa
        self.on_change = on_change

        cart_layout = QHBoxLayout(self)

        minus_button = QPushButton("-")
        minus_button.clicked.connect(lambda: self._set_quantity(self._current_quantity() - 1))
        minus_button.setProperty("class", "QuantityButton")
        cart_layout.addWidget(minus_button)

        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator(0, 99999, self))
        self.quantity_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quantity_input.setFixedWidth(60)
        self.quantity_input.setText(str(self._current_quantity()))
        self.quantity_input.editingFinished.connect(self._on_edit_finished)
        cart_layout.addWidget(self.quantity_input)

        plus_button = QPushButton("+")
        plus_button.clicked.connect(lambda: self._set_quantity(self._current_quantity() + 1))
        plus_button.setProperty("class", "QuantityButton")
        cart_layout.addWidget(plus_button)

    def _current_quantity(self) -> int:
        index = self.koszyk.check_if_offer_exists(self.EAN, self.hurtownia)
        if index != -1:
            return self.koszyk.get_oferty()[index].ilosc
        return 0

    def _on_edit_finished(self):
        text = self.quantity_input.text().strip()
        if not text:
            self.quantity_input.setText(str(self._current_quantity()))
            return
        self._set_quantity(int(text))

    def _set_quantity(self, new_quantity: int):
        if new_quantity < 0:
            self.quantity_input.setText(str(self._current_quantity()))
            return

        if new_quantity == self._current_quantity():
            self.quantity_input.setText(str(new_quantity))
            return

        self.koszyk.dodaj_oferte(self.EAN, self.hurtownia, new_quantity, self.nazwa)
        self.quantity_input.setText(str(new_quantity))
        if self.on_change:
            self.on_change()
