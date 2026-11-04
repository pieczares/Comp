from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from models.Produkt import Produkt
from ui.OffersTable import OffersTable


class ProductDetailsPage(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.produkt: Produkt | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        self.name_label = QLabel()
        self.name_label.setObjectName("PageTitle")
        self.name_label.setWordWrap(True)

        self.ean_label = QLabel()

        # Nazwa produktu i EAN mają być zwykłym tekstem.
        self.name_label.setTextFormat(Qt.TextFormat.PlainText)
        self.ean_label.setTextFormat(Qt.TextFormat.PlainText)

        self.offers_table = OffersTable()

        back_button = QPushButton("Wróć do oferty")
        back_button.clicked.connect(self.request_back)

        layout.addWidget(self.name_label)
        layout.addWidget(self.ean_label)
        layout.addWidget(self.offers_table)
        layout.addWidget(back_button)

    def set_product(self, produkt: Produkt):
        self.produkt = produkt

        self.name_label.setText(produkt.name)
        self.ean_label.setText(f"EAN: {produkt.EAN}")

        self.offers_table.set_offers(produkt.offers)


    def request_back(self):
        self.back_requested.emit()