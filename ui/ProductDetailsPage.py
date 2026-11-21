from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from models.Koszyk import Koszyk
from models.Produkt import Produkt
from models.Ulubione import Ulubione
from ui.OffersTable import OffersTable


class ProductDetailsPage(QWidget):
    HEART_FILLED = "♥"
    HEART_EMPTY = "♡"

    def __init__(self, go_to, koszyk: Koszyk, ulubione:Ulubione):
        super().__init__()
        self.koszyk = koszyk
        self.ulubione = ulubione

        self.produkt: Produkt | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        self.name_label = QLabel()
        self.name_label.setObjectName("PageTitle")
        self.name_label.setWordWrap(True)

        self.favorite_button = QPushButton(self.HEART_EMPTY)
        self.favorite_button.setFlat(True)
        self.favorite_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_button.setFixedSize(48, 48)
        self.favorite_button.setStyleSheet(
            "QPushButton { border: none; background: transparent; padding: 0;"
            " font-size: 30px; color: #e0245e; }"
            "QPushButton:hover { background: transparent; }"
        )
        self.favorite_button.clicked.connect(self.toggle_favorite)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.name_label, 1)
        header_layout.addWidget(
            self.favorite_button, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )

        self.ean_label = QLabel()

        # Nazwa produktu i EAN mają być zwykłym tekstem.
        self.name_label.setTextFormat(Qt.TextFormat.PlainText)
        self.ean_label.setTextFormat(Qt.TextFormat.PlainText)

        self.offers_table = OffersTable(self.koszyk)

        back_button = QPushButton("Wróć do oferty")
        back_button.clicked.connect(lambda : go_to("offers"))

        layout.addLayout(header_layout)
        layout.addWidget(self.ean_label)
        layout.addWidget(self.offers_table)
        layout.addWidget(back_button)

    def set_product(self, produkt: Produkt):
        self.produkt = produkt
        self.name_label.setText(produkt.name)
        self.ean_label.setText(f"EAN: {produkt.EAN}")

        self.offers_table.set_offers(produkt.offers, produkt.EAN, produkt.name)
        self.update_favorite_button()

    def is_favorite(self) -> bool:
        return (
            self.produkt is not None
            and self.ulubione.check_if_product_exists(self.produkt.EAN) != -1
        )

    def update_favorite_button(self):
        if self.is_favorite():
            self.favorite_button.setText(self.HEART_FILLED)
            self.favorite_button.setToolTip("Usuń z ulubionych")
        else:
            self.favorite_button.setText(self.HEART_EMPTY)
            self.favorite_button.setToolTip("Dodaj do ulubionych")

    def toggle_favorite(self):
        if self.produkt is None:
            return
        if self.is_favorite():
            self.ulubione.usun_produkt(self.produkt)
        else:
            self.ulubione.dodaj_produkt(self.produkt)
        self.update_favorite_button()
