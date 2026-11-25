from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView, QHeaderView, QTableWidgetItem, QTableWidget, QWidget,
)

from models.Koszyk import Koszyk
from models.Oferta import Oferta
from ui.QuantityChanger import QuantityChanger


class OffersTable(QTableWidget):
    COL_QTY = 4
    QTY_MIN_WIDTH = 170
    ROW_PADDING = 8

    def __init__(self, koszyk: Koszyk):
        super().__init__()
        self.koszyk = koszyk

        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            "Hurtownia",
            "Cena netto",
            "Cena brutto",
            "Jednostka",
            "W koszyku",
        ])

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()

        # Nazwa hurtowni zajmuje pozostałe dostępne miejsce.
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )

        for column in range(1, self.COL_QTY):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )
        header.setSectionResizeMode(self.COL_QTY, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(self.COL_QTY, self.QTY_MIN_WIDTH)
        header.sectionResized.connect(self._schedule_fit_rows)

    def _schedule_fit_rows(self, *args):
        QTimer.singleShot(0, self._fit_rows)

    def _fit_rows(self):
        # Wysokość = większa z: wysokość tekstu i wysokość widgetu.
        for row in range(self.rowCount()):
            self.resizeRowToContents(row)
            needed = self.rowHeight(row)
            widget = self.cellWidget(row, self.COL_QTY)
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

    def set_offers(self, offers: list[Oferta], EAN: str, nazwa: str = ""):
        sorted_offers = sorted(
            offers,
            key=lambda oferta: oferta.cena_brutto,
        )

        # Usuń poprzednie dane, zachowując nagłówki.
        self.clearContents()
        self.setRowCount(len(sorted_offers))

        qty_width = self.QTY_MIN_WIDTH

        for row, oferta in enumerate(sorted_offers):
            self.setItem(
                row, 0, QTableWidgetItem(str(oferta.hurtownia))
            )

            netto = QTableWidgetItem(
                f"{oferta.cena_netto:.2f} zł"
            )
            brutto = QTableWidgetItem(
                f"{oferta.cena_brutto:.2f} zł"
            )

            alignment = (
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter
            )

            netto.setTextAlignment(alignment)
            brutto.setTextAlignment(alignment)

            self.setItem(row, 1, netto)
            self.setItem(row, 2, brutto)
            self.setItem(row, 3, QTableWidgetItem(oferta.jednostka))

            changer = QuantityChanger(
                self.koszyk, EAN, oferta.hurtownia, nazwa
            )
            w, _ = self._lock_min_size(changer)
            qty_width = max(qty_width, w + 8)
            self.setCellWidget(row, self.COL_QTY, changer)

        self.setColumnWidth(self.COL_QTY, qty_width)
        self._fit_rows()
        self._schedule_fit_rows()
