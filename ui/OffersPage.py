from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QScrollArea, QGridLayout, QComboBox
from integrations.Produkt_api import ProduktApi
from ui.ProductCard import ProductCard


class OffersPage(QWidget):
    def __init__(self, go_to):
        super().__init__()
        self.__quantity = "20"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Przeglądaj ofertę")
        title.setObjectName("PageTitle")

        back_button = QPushButton("Wróć do strony głównej")
        back_button.clicked.connect(lambda: go_to("home"))

        quantity_combo = QComboBox()
        quantity_combo.addItems(["20", "50", "100"])
        quantity_combo.setCurrentText(self.__quantity)
        quantity_combo.currentIndexChanged.connect(self.quantity_changed)

        layout.addStretch()


        cards_container = QWidget()
        self.cards_layout = QGridLayout(cards_container)
        self.cards_layout.setSpacing(14)


        products = ProduktApi.pobierz_produkty_api(f"http://127.0.0.1:8000/produkty?&limit={self.__quantity}&offset=0")
        row = 0
        col = 0

        for produkt in products:
            self.cards_layout.addWidget(ProductCard(produkt), row, col)
            col+= 1
            if col == 3:
                col = 0
                row += 1

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(cards_container)

        layout.addWidget(title)
        layout.addWidget(scroll)
        layout.addWidget(back_button)

        layout.addWidget(quantity_combo)

    def quantity_changed(self, index):
        new_quantity = int(self.sender().itemText(index))
        if new_quantity != self.__quantity:
            self.__quantity = new_quantity
            self.refresh_products_list()

    def refresh_products_list(self):
        # usuń wszystkie karty z layoutu
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        # dodaj karty ponownie
        products = ProduktApi.pobierz_produkty_api(f"http://127.0.0.1:8000/produkty?&limit={self.__quantity}&offset=0")
        for produkt in products:
            card = ProductCard(
                produkt=produkt,
            )
            self.cards_layout.addWidget(card)

        # self.cards_layout.addStretch()