from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView, QHeaderView, QPushButton, QTableWidget, QTableWidgetItem,
    QWidget,
)

from integrations.Produkt_api import BladApi
from models.Koszyk import Koszyk
from models.ProduktWKoszyku import ProduktWKoszyku
from ui.QuantityChanger import QuantityChanger


class CartTable(QTableWidget):
    COLUMNS = [
        "Hurtownia", "Nazwa produktu", "Cena netto",
        "Cena brutto", "Jednostka", "W koszyku", "",
    ]
    COL_QTY = 5
    COL_REMOVE = 6
    ROW_PADDING = 8

    def __init__(self, koszyk: Koszyk, on_change=None):
        super().__init__()
        self.koszyk = koszyk
        self.on_change = on_change
        # Komunikat o ostatnim błędzie pobierania cen (None = wszystko w porządku).
        self.error_message: str | None = None

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
        vheader.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in (2, 3, 4):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.COL_QTY, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_REMOVE, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(self.COL_QTY, 170)
        self.setColumnWidth(self.COL_REMOVE, 90)
        header.sectionResized.connect(self._schedule_fit_rows)

    def _schedule_fit_rows(self, *args):
        QTimer.singleShot(0, self._fit_rows)

    def _fit_rows(self):
        # Wysokość = większa z: wysokość zawiniętego tekstu i wysokość widgetów.
        for row in range(self.rowCount()):
            self.resizeRowToContents(row)
            needed = self.rowHeight(row)
            for col in (self.COL_QTY, self.COL_REMOVE):
                widget = self.cellWidget(row, col)
                if widget is not None:
                    needed = max(needed, widget.minimumHeight() + self.ROW_PADDING)
            self.setRowHeight(row, needed)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._schedule_fit_rows()

    def showEvent(self, event):
        super().showEvent(event)
        self._schedule_fit_rows()

    @staticmethod
    def _lock_min_size(widget: QWidget) -> tuple[int, int]:
        for w in [widget, *widget.findChildren(QWidget)]:
            w.ensurePolished()
        layout = widget.layout()
        if layout is not None:
            layout.activate()
        hint = widget.sizeHint()
        widget.setMinimumSize(hint)
        return hint.width(), hint.height()

    def populate_table(self):
        oferty = list(self.koszyk.get_oferty())
        self.clearContents()
        self.setRowCount(len(oferty))
        right = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        qty_width = 170
        remove_width = 90

        self.error_message = None

        for row, oferta in enumerate(oferty):

            # Po pierwszym błędzie nie pytamy serwera dalej (unikamy wielu timeoutów).
            if self.error_message is None:
                try:
                    oferta.pobierz_ceny()
                except BladApi as e:
                    self.error_message = str(e)
            ceny_ok = self.error_message is None

            self.setItem(row, 0, QTableWidgetItem(oferta.hurtownia))
            self.setItem(row, 1, QTableWidgetItem(oferta.nazwa or oferta.EAN))

            netto = QTableWidgetItem(f"{oferta.cena_netto:.2f} zł" if ceny_ok else "—")
            brutto = QTableWidgetItem(f"{oferta.cena_brutto:.2f} zł" if ceny_ok else "—")
            netto.setTextAlignment(right)
            brutto.setTextAlignment(right)
            self.setItem(row, 2, netto)
            self.setItem(row, 3, brutto)
            self.setItem(row, 4, QTableWidgetItem(oferta.jednostka if ceny_ok else "—"))

            changer = QuantityChanger(
                self.koszyk, oferta.EAN, oferta.hurtownia,
                oferta.nazwa, on_change=self._schedule_refresh,
            )
            w, _ = self._lock_min_size(changer)
            qty_width = max(qty_width, w + 8)
            self.setCellWidget(row, self.COL_QTY, changer)

            remove_button = QPushButton("Usuń")
            remove_button.clicked.connect(
                lambda _=False, o=oferta: self.remove_offer(o)
            )
            w, _ = self._lock_min_size(remove_button)
            remove_width = max(remove_width, w + 8)
            self.setCellWidget(row, self.COL_REMOVE, remove_button)

        self.setColumnWidth(self.COL_QTY, qty_width)
        self.setColumnWidth(self.COL_REMOVE, remove_width)
        self._fit_rows()
        self._schedule_fit_rows()

    def _schedule_refresh(self):
        QTimer.singleShot(0, self._refresh)

    def _refresh(self):
        self.populate_table()
        if self.on_change:
            self.on_change()

    def remove_offer(self, oferta: ProduktWKoszyku):
        self.koszyk.usun_oferte(oferta.EAN, oferta.hurtownia)
        self._schedule_refresh()
