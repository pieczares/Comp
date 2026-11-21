from typing import Final

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QScrollArea, QGridLayout, QComboBox, \
    QHBoxLayout
from integrations.Produkt_api import ProduktApi
from models.Ulubione import Ulubione
from ui.ProductCard import ProductCard


class OffersPage(QWidget):
    product_selected = Signal(object)

    def __init__(self, ulubione:Ulubione, go_to):
        super().__init__()
        self.ulubione = ulubione

        self.__quantity = "20"
        self.__offset = 0
        self.__products_count: Final[int] = ProduktApi().pobierz_produkty_count_api()

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
        for column in range(3):
            self.cards_layout.setColumnStretch(column, 1)

        self.add_product_cards()

        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setSizeAdjustPolicy(QScrollArea.SizeAdjustPolicy.AdjustToContents)
        scroll.setWidgetResizable(True)
        scroll.setWidget(cards_container)

        self.prev_button = QPushButton("Poprzednia strona")
        self.prev_button.clicked.connect(self.previous)
        self.prev_button.setEnabled(False)

        self.next_button = QPushButton("Następna strona")
        self.next_button.clicked.connect(self.next)
        self.next_button.setEnabled(True)

        self.page_number_label = QLabel("1")
        #tymczasowo zmieniam kolor na żółty, bo nie widać numeru strony przy ciemnym motywie
        self.page_number_label.setStyleSheet("color: yellow")

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
        products = ProduktApi().pobierz_produkty_api(limit=self.__quantity, offset=self.__offset)
        row = 0
        col = 0

        for produkt in products:
            widget = ProductCard(produkt, self.ulubione)
            widget.setObjectName("ProductCard")
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
        page_number = (self.__offset // int(self.__quantity)) + 1
        self.page_number_label.setText(str(page_number))

        if self.__offset+int(self.__quantity) >= self.__products_count:
            self.next_button.setEnabled(False)
        else:
            self.next_button.setEnabled(True)

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
