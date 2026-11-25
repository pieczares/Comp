from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QScrollArea, QGridLayout, QComboBox, \
    QHBoxLayout
from loaders.OffersLoader import OffersLoader
from loaders.ProductsLoader import ProductsLoader
from models.Ulubione import Ulubione
from ui.ProductCard import ProductCard
from ui.ProductPlaceholder import ProductPlaceholder


class OffersPage(QWidget):
    product_selected = Signal(object)

    # Ile szkieletów kart pokazujemy w trakcie ładowania.
    PLACEHOLDER_COUNT = 20
    COLUMNS = 3

    def __init__(self, ulubione: Ulubione, go_to):
        super().__init__()
        self.ulubione = ulubione

        self._quantity = 20
        self._offset = 0
        self._request_id = 0
        self._loading = False
        self._loaded = False
        # Liczbę produktów pobiera ProductsLoader przy pierwszym ładowaniu (nie blokujemy GUI).
        self._products_count: int | None = None
        self._loader: ProductsLoader | None = None
        self._offers_loader: OffersLoader | None = None
        self._cards: dict[str, list[ProductCard]] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Przeglądaj ofertę")
        title.setObjectName("PageTitle")

        self.loading_label = QLabel("Ładowanie produktów…")
        self.loading_label.hide()

        self.empty_label = QLabel("Brak produktów do wyświetlenia.")
        self.empty_label.hide()

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

        self.quantity_combo = QComboBox()
        self.quantity_combo.addItems(["20", "50", "100"])
        self.quantity_combo.setCurrentText(str(self._quantity))
        self.quantity_combo.currentIndexChanged.connect(self.quantity_changed)

        cards_container = QWidget()
        self.cards_layout = QGridLayout(cards_container)
        self.cards_layout.setSpacing(14)
        for column in range(self.COLUMNS):
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
        layout.addWidget(self.loading_label)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.error_label)
        layout.addWidget(self.retry_button)
        layout.addWidget(scroll)
        layout.addLayout(nav_menu_layout)
        layout.addWidget(self.quantity_combo)
        layout.addWidget(back_button)

    def showEvent(self, event):
        super().showEvent(event)
        # Ładujemy tylko raz (lub ponownie po błędzie) – powrót z karty produktu nie kasuje listy.
        if not self._loaded and not self._loading:
            self.load_products()

    def _cancel_loaders(self):
        for loader in (self._loader, self._offers_loader):
            if loader is not None:
                loader.anuluj()
        self._loader = None
        self._offers_loader = None

    def load_products(self):
        self._request_id += 1
        self._cancel_loaders()

        self.clear_cards()
        self.hide_error()
        self.empty_label.hide()
        self._loading = True
        self._loaded = False
        self.loading_label.show()
        self.add_placeholders()
        self.update_navigation()

        loader = ProductsLoader(
            self._request_id,
            limit=self._quantity,
            offset=self._offset,
            liczba_produktow=self._products_count,
        )
        loader.done.connect(self.on_products_loaded)
        loader.failed.connect(self.on_products_failed)
        self._loader = loader
        loader.start()

    def on_products_loaded(self, token: int, wynik):
        if token != self._request_id:
            return
        liczba, produkty = wynik
        self._products_count = liczba
        self.finish_loading()
        self._loaded = True
        self.clear_cards()

        if not produkty:
            if self._offset > 0:
                # Strona poza zakresem (np. dane na serwerze się zmniejszyły) – wracamy na początek.
                self._offset = 0
                self.load_products()
            else:
                self.empty_label.show()
            return

        self.add_product_cards(produkty)
        self.load_offers(produkty)

    def on_products_failed(self, token: int, message: str):
        if token != self._request_id:
            return
        self.finish_loading()
        self.clear_cards()
        self.show_error(message)

    def load_offers(self, produkty):
        loader = OffersLoader(self._request_id, [produkt.EAN for produkt in produkty])
        loader.item.connect(self.on_offers_loaded)
        self._offers_loader = loader
        loader.start()

    def on_offers_loaded(self, token: int, ean: str, oferty, blad):
        if token != self._request_id:
            return
        for card in self._cards.get(ean, []):
            if oferty is None:
                card.produkt.set_offers_error(blad or "Nieznany błąd.")
            else:
                card.produkt.set_offers(oferty)
            card.refresh()

    def finish_loading(self):
        self._loading = False
        self.loading_label.hide()
        self.update_navigation()

    def show_error(self, message: str):
        self.error_label.setText(f"Błąd serwera: {message}")
        self.error_label.show()
        self.retry_button.show()

    def hide_error(self):
        self.error_label.hide()
        self.retry_button.hide()

    def add_placeholders(self):
        for index in range(self.PLACEHOLDER_COUNT):
            self.cards_layout.addWidget(ProductPlaceholder(), index // self.COLUMNS, index % self.COLUMNS)

    def add_product_cards(self, products):
        row = 0
        col = 0

        for produkt in products:
            widget = ProductCard(produkt, self.ulubione)
            widget.setObjectName("ProductCard")
            widget.details_requested.connect(self.product_selected.emit)
            self._cards.setdefault(produkt.EAN, []).append(widget)
            self.cards_layout.addWidget(widget, row, col)
            col += 1
            if col == self.COLUMNS:
                col = 0
                row += 1

    def clear_cards(self):
        # usuń wszystkie karty i placeholdery z layoutu
        self._cards.clear()
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.hide()
                widget.deleteLater()

    def update_navigation(self):
        quantity = self._quantity
        loading = self._loading
        self.page_number_label.setText(str(self._offset // quantity + 1))
        self.quantity_combo.setEnabled(not loading)
        self.prev_button.setEnabled(not loading and self._offset > 0)
        total = self._products_count
        self.next_button.setEnabled(
            not loading and total is not None and self._offset + quantity < total
        )

    def quantity_changed(self, index):
        new_quantity = int(self.quantity_combo.itemText(index))
        if new_quantity != self._quantity:
            self._quantity = new_quantity
            self._offset = 0
            self.load_products()

    def next(self):
        self._offset += self._quantity
        self.load_products()

    def previous(self):
        self._offset = max(0, self._offset - self._quantity)
        self.load_products()
