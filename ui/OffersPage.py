from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QScrollArea, QGridLayout, QComboBox, \
    QHBoxLayout
from integrations.Produkt_api import BladApi, ProduktApi
from models.Ulubione import Ulubione
from ui.ProductCard import ProductCard


class OffersPage(QWidget):
    product_selected = Signal(object)

    def __init__(self, ulubione:Ulubione, go_to):
        super().__init__()
        self.ulubione = ulubione

        self.__quantity = "20"
        self.__offset = 0
        self.__products_count: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Przeglądaj ofertę")
        title.setObjectName("PageTitle")

        self.error_label = QLabel()
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setTextFormat(Qt.TextFormat.PlainText)
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        self.retry_button = QPushButton("Spróbuj ponownie")
        self.retry_button.clicked.connect(self.load_products)
        self.retry_button.hide()

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
        self.next_button.setEnabled(False)

        self.page_number_label = QLabel("1")
        #tymczasowo zmieniam kolor na żółty, bo nie widać numeru strony przy ciemnym motywie
        self.page_number_label.setStyleSheet("color: yellow")

        nav_menu_layout = QHBoxLayout()
        nav_menu_layout.addWidget(self.prev_button)
        nav_menu_layout.addWidget(self.page_number_label)
        nav_menu_layout.addWidget(self.next_button)

        layout.addWidget(title)
        layout.addWidget(self.error_label)
        layout.addWidget(self.retry_button)
        layout.addWidget(scroll)
        layout.addWidget(back_button)
        layout.addLayout(nav_menu_layout)
        layout.addWidget(quantity_combo)

        self.load_products()

    def load_products(self):
        self.clear_cards()
        try:
            if self.__products_count is None:
                self.__products_count = ProduktApi().pobierz_produkty_count_api()
            products = ProduktApi().pobierz_produkty_api(
                limit=self.__quantity, offset=self.__offset
            )
        except BladApi as e:
            self.show_error(str(e))
        else:
            self.hide_error()
            self.add_product_cards(products)
        self.update_navigation()

    def show_error(self, message: str):
        self.error_label.setText(f"Błąd serwera: {message}")
        self.error_label.show()
        self.retry_button.show()

    def hide_error(self):
        self.error_label.hide()
        self.retry_button.hide()

    def add_product_cards(self, products):
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

    def clear_cards(self):
        # usuń wszystkie karty z layoutu
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.hide()
                widget.deleteLater()

    def update_navigation(self):
        quantity = int(self.__quantity)
        self.page_number_label.setText(str(self.__offset // quantity + 1))
        self.prev_button.setEnabled(self.__offset > 0)
        total = self.__products_count
        self.next_button.setEnabled(total is not None and self.__offset + quantity < total)

    def quantity_changed(self, index):
        new_quantity = self.sender().itemText(index)
        if new_quantity != str(self.__quantity):
            self.__quantity = new_quantity
            self.__offset = 0
            self.load_products()

    def next(self):
        self.__offset += int(self.__quantity)
        self.load_products()

    def previous(self):
        self.__offset = max(0, self.__offset - int(self.__quantity))
        self.load_products()
