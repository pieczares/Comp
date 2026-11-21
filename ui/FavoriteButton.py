from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from models.Produkt import Produkt
from models.Ulubione import Ulubione


class FavoriteButton(QPushButton):
    HEART_FILLED = "♥"
    HEART_EMPTY = "♡"

    def __init__(self, ulubione: Ulubione, produkt: Produkt | None = None, parent=None):
        super().__init__(self.HEART_EMPTY, parent)
        self.ulubione = ulubione
        self.produkt = produkt

        # Wygląd przycisku jest zdefiniowany w style.qss (#FavoriteButton).
        self.setObjectName("FavoriteButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self.toggle)

        self.update_state()

    def set_produkt(self, produkt: Produkt):
        self.produkt = produkt
        self.update_state()

    def is_favorite(self) -> bool:
        return (
            self.produkt is not None
            and self.ulubione.check_if_product_exists(self.produkt.EAN) != -1
        )

    def update_state(self):
        if self.is_favorite():
            self.setText(self.HEART_FILLED)
            self.setToolTip("Usuń z ulubionych")
        else:
            self.setText(self.HEART_EMPTY)
            self.setToolTip("Dodaj do ulubionych")

    def toggle(self):
        if self.produkt is None:
            return
        if self.is_favorite():
            self.ulubione.usun_produkt(self.produkt)
        else:
            self.ulubione.dodaj_produkt(self.produkt)
        self.update_state()

    def showEvent(self, event):
        super().showEvent(event)
        # Stan mógł się zmienić na innej stronie (np. szczegóły produktu).
        self.update_state()
