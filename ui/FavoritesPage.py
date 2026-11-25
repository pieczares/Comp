from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHeaderView, QLabel, QPushButton, QScrollArea,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout,
)

from loaders.OffersLoader import OffersLoader
from models.Oferta import Oferta
from models.Produkt import Produkt
from models.Ulubione import Ulubione
from ui.FavoriteButton import FavoriteButton


class FavoritesPage(QWidget):
    COLUMNS = ["Hurtownia", "Cena netto", "Cena brutto", "Jednostka"]

    def __init__(self, go_to, ulubione: Ulubione):
        super().__init__()
        self.ulubione = ulubione

        self._token = 0
        self._loader: OffersLoader | None = None
        # EAN -> lista (layout na oferty, produkt); uzupełniane, gdy przyjdą oferty.
        self._holders: dict[str, list[tuple[QVBoxLayout, Produkt]]] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Ulubione")
        title.setObjectName("PageTitle")

        self.empty_label = QLabel("Nie masz jeszcze ulubionych produktów.")

        container = QWidget()
        self.items_layout = QVBoxLayout(container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(16)

        self.scroll = QScrollArea()
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(container)

        back_button = QPushButton("Wróć do strony głównej")
        back_button.clicked.connect(lambda: go_to("home"))

        layout.addWidget(title)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.scroll)
        layout.addWidget(back_button)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_favorites()

    def update_favorites(self):
        self._token += 1
        if self._loader is not None:
            self._loader.anuluj()
            self._loader = None
        self._holders.clear()

        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.deleteLater()

        produkty = list(self.ulubione.produkty)
        self.empty_label.setVisible(not produkty)
        self.scroll.setVisible(bool(produkty))

        for produkt in produkty:
            self.items_layout.addWidget(self._create_item(produkt))
        self.items_layout.addStretch()

        if produkty:
            loader = OffersLoader(self._token, [produkt.EAN for produkt in produkty])
            loader.item.connect(self._on_offers)
            self._loader = loader
            loader.start()

    def _on_offers(self, token: int, ean: str, oferty, blad):
        if token != self._token:
            return
        for holder, produkt in self._holders.get(ean, []):
            if oferty is None:
                produkt.set_offers_error(blad or "Nieznany błąd.")
                self._render_offers(holder, produkt, f"Nie udało się pobrać ofert: {blad}")
            else:
                produkt.set_offers(oferty)
                self._render_offers(holder, produkt)

    def _create_item(self, produkt: Produkt) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        hlayout = QHBoxLayout()

        name_label = QLabel(produkt.name)
        name_label.setObjectName("ProductName")
        name_label.setWordWrap(True)
        name_label.setTextFormat(Qt.TextFormat.PlainText)

        fav_button = FavoriteButton(self.ulubione, produkt)

        hlayout.addWidget(name_label)
        hlayout.addStretch()
        hlayout.addWidget(fav_button)

        ean_label = QLabel(f"Kod: {produkt.EAN}")
        ean_label.setTextFormat(Qt.TextFormat.PlainText)

        layout.addLayout(hlayout)
        layout.addWidget(ean_label)

        holder = QVBoxLayout()
        holder.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(holder)
        self._holders.setdefault(produkt.EAN, []).append((holder, produkt))

        # Ostatnio znane oferty (z zapisu) pokazujemy od razu, reszta w tle.
        self._render_offers(holder, produkt, None if produkt.offers else "Ładowanie ofert…")

        return frame

    def _render_offers(self, holder: QVBoxLayout, produkt: Produkt, status: str | None = None):
        while holder.count():
            item = holder.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.deleteLater()

        if status:
            label = QLabel(status)
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setWordWrap(True)
            holder.addWidget(label)
        elif produkt.offers:
            holder.addWidget(self._create_offers_table(produkt.offers))
        else:
            holder.addWidget(QLabel("Brak dostępnych ofert"))

    def _create_offers_table(self, offers: list[Oferta]) -> QTableWidget:
        sorted_offers = sorted(offers, key=lambda o: o.hurtownia.lower())
        right = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        table = QTableWidget(len(sorted_offers), len(self.COLUMNS))
        table.setHorizontalHeaderLabels(self.COLUMNS)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in range(1, len(self.COLUMNS)):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)

        for row, oferta in enumerate(sorted_offers):
            netto = QTableWidgetItem(f"{oferta.cena_netto:.2f} zł")
            brutto = QTableWidgetItem(f"{oferta.cena_brutto:.2f} zł")
            netto.setTextAlignment(right)
            brutto.setTextAlignment(right)

            table.setItem(row, 0, QTableWidgetItem(str(oferta.hurtownia)))
            table.setItem(row, 1, netto)
            table.setItem(row, 2, brutto)
            table.setItem(row, 3, QTableWidgetItem(oferta.jednostka))

        table.resizeRowsToContents()
        height = header.sizeHint().height() + 2 * table.frameWidth()
        height += sum(table.rowHeight(row) for row in range(table.rowCount()))
        table.setFixedHeight(height)

        return table
