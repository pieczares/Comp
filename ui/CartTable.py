from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView, QHeaderView, QPushButton, QTableWidget, QTableWidgetItem,
    QWidget,
)

from integrations.Produkt_api import ProduktApi
from models.Koszyk import Koszyk
from models.Oferta import Oferta
from models.ProduktWKoszyku import ProduktWKoszyku
from ui.QuantityChanger import QuantityChanger


class CartTable(QTableWidget):
    COLUMNS = [
        "Hurtownia", "Nazwa produktu", "Cena netto",
        "Cena brutto", "Jednostka", "W koszyku", "",
    ]
    COL_QTY = 5
    COL_REMOVE = 6
    MIN_QTY_WIDTH = 170
    MIN_REMOVE_WIDTH = 90

    def __init__(self, koszyk: Koszyk, on_change=None):
        super().__init__()
        self.koszyk = koszyk
        self.on_change = on_change
        self._cache: dict[tuple[str, str], Oferta] = {}

        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        vheader = self.verticalHeader()
        vheader.setVisible(False)
        vheader.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in (2, 3, 4):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        # Kolumny z widgetami mają stałą szerokość (ResizeToContents liczyło je
        # z niespolishowanych widgetów i je zwężało po odświeżeniu).
        header.setSectionResizeMode(self.COL_QTY, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_REMOVE, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(self.COL_QTY, self.MIN_QTY_WIDTH)
        self.setColumnWidth(self.COL_REMOVE, self.MIN_REMOVE_WIDTH)
        header.sectionResized.connect(self._schedule_row_resize)

    def _schedule_row_resize(self, *args):
        QTimer.singleShot(0, self.resizeRowsToContents)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._schedule_row_resize()

    def showEvent(self, event):
        super().showEvent(event)
        self._schedule_row_resize()

    @staticmethod
    def _polished_width(widget: QWidget) -> int:
        for w in [widget, *widget.findChildren(QWidget)]:
            w.ensurePolished()
        layout = widget.layout()
        if layout is not None:
            layout.activate()
        return widget.sizeHint().width()

    def _get_price(self, oferta: ProduktWKoszyku) -> Oferta | None:
        key = (oferta.hurtownia, oferta.EAN)
        if key not in self._cache:
            try:
                self._cache[key] = ProduktApi.pobierz_cene_api(
                    oferta.hurtownia, oferta.EAN
                )
            except Exception as e:
                print(f"Błąd pobierania ceny {key}: {e}")
                return None
        return self._cache[key]

    def populate_table(self):
        oferty = list(self.koszyk.get_oferty())
        self.clearContents()
        self.setRowCount(len(oferty))
        right = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        qty_width = self.MIN_QTY_WIDTH
        remove_width = self.MIN_REMOVE_WIDTH

        for row, oferta in enumerate(oferty):
            cena = self._get_price(oferta)

            self.setItem(row, 0, QTableWidgetItem(oferta.hurtownia))
            self.setItem(row, 1, QTableWidgetItem(oferta.nazwa or oferta.EAN))

            if cena is None:
                for col in (2, 3, 4):
                    self.setItem(row, col, QTableWidgetItem("—"))
            else:
                netto = QTableWidgetItem(f"{cena.cena_netto:.2f} zł")
                brutto = QTableWidgetItem(f"{cena.cena_brutto:.2f} zł")
                netto.setTextAlignment(right)
                brutto.setTextAlignment(right)
                self.setItem(row, 2, netto)
                self.setItem(row, 3, brutto)
                self.setItem(row, 4, QTableWidgetItem(cena.jednostka))

            changer = QuantityChanger(
                self.koszyk, oferta.EAN, oferta.hurtownia,
                oferta.nazwa, on_change=self._schedule_refresh,
            )
            self.setCellWidget(row, self.COL_QTY, changer)
            qty_width = max(qty_width, self._polished_width(changer) + 8)

            remove_button = QPushButton("Usuń")
            remove_button.clicked.connect(
                lambda _=False, o=oferta: self.remove_offer(o)
            )
            self.setCellWidget(row, self.COL_REMOVE, remove_button)
            remove_width = max(remove_width, self._polished_width(remove_button) + 8)

        self.setColumnWidth(self.COL_QTY, qty_width)
        self.setColumnWidth(self.COL_REMOVE, remove_width)
        self.resizeRowsToContents()
        self._schedule_row_resize()

    def _schedule_refresh(self):
        QTimer.singleShot(0, self._refresh)

    def _refresh(self):
        self.populate_table()
        if self.on_change:
            self.on_change()

    def remove_offer(self, oferta: ProduktWKoszyku):
        self.koszyk.usun_oferte(oferta.EAN, oferta.hurtownia)
        self._schedule_refresh()
