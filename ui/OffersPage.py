from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QScrollArea

from integrations.Produkt_api import ProduktApi
from ui.ProductCard import ProductCard


class OffersPage(QWidget):
    def __init__(self, go_to):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Przeglądaj ofertę")
        title.setObjectName("PageTitle")

        back_button = QPushButton("Wróć do strony głównej")
        back_button.clicked.connect(lambda: go_to("home"))

        layout.addStretch()


        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setSpacing(14)

        products = ProduktApi.pobierz_produkty_api("http://127.0.0.1:8000/produkty")

        for produkt in products:
            cards_layout.addWidget(ProductCard(produkt))

        cards_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(cards_container)

        layout.addWidget(title)
        layout.addWidget(scroll)
        layout.addWidget(back_button)