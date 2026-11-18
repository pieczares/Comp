from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView, QHeaderView, QPushButton, QTableWidget, QTableWidgetItem,
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
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in range(2, len(self.COLUMNS)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

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

            self.setCellWidget(
                row, 5,
                QuantityChanger(
                    self.koszyk, oferta.EAN, oferta.hurtownia,
                    oferta.nazwa, on_change=self._schedule_refresh,
                ),
            )

            remove_button = QPushButton("Usuń")
            remove_button.clicked.connect(
                lambda _=False, o=oferta: self.remove_offer(o)
            )
            self.setCellWidget(row, 6, remove_button)

        self.resizeRowsToContents()

    def _schedule_refresh(self):
        QTimer.singleShot(0, self._refresh)

    def _refresh(self):
        self.populate_table()
        if self.on_change:
            self.on_change()

    def remove_offer(self, oferta: ProduktWKoszyku):
        self.koszyk.usun_oferte(oferta.EAN, oferta.hurtownia)
        self._schedule_refresh()
