from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from loaders.OffersLoader import OffersLoader
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
        self._token = 0
        self._loader: OffersLoader | None = None

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

        self.status_label = QLabel()
        self.status_label.setTextFormat(Qt.TextFormat.PlainText)
        self.status_label.setWordWrap(True)
        self.status_label.hide()

        self.name_label.setTextFormat(Qt.TextFormat.PlainText)
        self.ean_label.setTextFormat(Qt.TextFormat.PlainText)

        self.offers_table = OffersTable(self.koszyk)

        back_button = QPushButton("Wróć do oferty")
        back_button.clicked.connect(lambda : go_to("offers"))

        layout.addLayout(header_layout)
        layout.addWidget(self.ean_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.offers_table)
        layout.addWidget(back_button)

    def set_product(self, produkt: Produkt):
        self._token += 1
        if self._loader is not None:
            self._loader.anuluj()
            self._loader = None

        self.produkt = produkt
        self.name_label.setText(produkt.name)
        self.ean_label.setText(f"EAN: {produkt.EAN}")
        self.favorite_button.set_produkt(produkt)
        self.status_label.hide()

        if produkt.offers_loaded:
            self.offers_table.set_offers(produkt.offers, produkt.EAN, produkt.name)
            return

        # Oferty jeszcze nie przyszły (lub poprzednio był błąd) – pobieramy w tle.
        self.offers_table.set_offers([], produkt.EAN, produkt.name)
        self.status_label.setText("Ładowanie ofert…")
        self.status_label.show()

        loader = OffersLoader(self._token, [produkt.EAN])
        loader.item.connect(self._on_offers)
        self._loader = loader
        loader.start()

    def _on_offers(self, token: int, ean: str, oferty, blad):
        if token != self._token or self.produkt is None or self.produkt.EAN != ean:
            return
        if oferty is None:
            self.produkt.set_offers_error(blad or "Nieznany błąd.")
            self.status_label.setText(f"Nie udało się pobrać ofert: {blad}")
            self.status_label.show()
            return
        self.produkt.set_offers(oferty)
        self.status_label.hide()
        self.offers_table.set_offers(self.produkt.offers, self.produkt.EAN, self.produkt.name)
