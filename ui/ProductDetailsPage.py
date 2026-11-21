from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from models.Koszyk import Koszyk
from models.Produkt import Produkt
from models.Ulubione import Ulubione
from ui.FavoriteButton import FavoriteButton
from ui.OffersTable import OffersTable


class ProductDetailsPage(QWidget):

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

        self.favorite_button = FavoriteButton(self.ulubione)

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
        self.favorite_button.set_produkt(produkt)
