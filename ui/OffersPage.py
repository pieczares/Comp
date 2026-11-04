from typing import Final

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QScrollArea, QGridLayout, QComboBox, \
    QHBoxLayout
from integrations.Produkt_api import ProduktApi
from ui.ProductCard import ProductCard


class OffersPage(QWidget):
    product_selected = Signal(object)

    def __init__(self, go_to):
        super().__init__()
        self.__quantity = "20"
        self.__offset = 0
        self.__products_count: Final[int] = ProduktApi.pobierz_produkty_count_api("http://127.0.0.1:8000/produkty/count")

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

        self.add_product_cards()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(cards_container)

        self.prev_button = QPushButton("Poprzednia strona")
        self.prev_button.clicked.connect(self.previous)

        self.next_button = QPushButton("Następna strona")
        self.next_button.clicked.connect(self.next)

        self.page_number_label = QLabel("1")

        nav_menu_layout = QHBoxLayout()
        nav_menu_layout.addWidget(self.prev_button)
        nav_menu_layout.addWidget(self.page_number_label)
        nav_menu_layout.addWidget(self.next_button)

        layout.addWidget(title)
        layout.addWidget(scroll)
        layout.addWidget(back_button)
        layout.addLayout(nav_menu_layout)
        layout.addWidget(quantity_combo)


    def add_product_cards(self):
        products = ProduktApi.pobierz_produkty_api(f"http://127.0.0.1:8000/produkty?&limit={self.__quantity}&offset={self.__offset}")
        row = 0
        col = 0

        for produkt in products:
            widget = ProductCard(produkt)
            widget.details_requested.connect(self.product_selected.emit)
            self.cards_layout.addWidget(widget, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

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
                widget.hide()
                widget.deleteLater()

        self.add_product_cards()
        # zmień numer strony !!!!!!!!!!!!!!!!!

    def next(self):
        current_page = int(self.page_number_label.text())
        self.page_number_label.setText(str(current_page + 1))
        self.__offset = current_page * int(self.__quantity)
        self.refresh_products_list()
        self.prev_button.setEnabled(True)
        if self.__offset+int(self.__quantity) >= self.__products_count:
            self.next_button.setEnabled(False)

    def previous(self):
        current_page = int(self.page_number_label.text())
        self.next_button.setEnabled(True)
        if current_page > 1:
            self.page_number_label.setText(str(current_page - 1))
            self.__offset = (current_page - 2 ) * int(self.__quantity)
            self.refresh_products_list()
        else:
            self.prev_button.setEnabled(False)
