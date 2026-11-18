from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem, QTableWidget

from models.Koszyk import Koszyk
from models.Oferta import Oferta
from ui.QuantityChanger import QuantityChanger


class OffersTable(QTableWidget):
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

        for column in range(1, 5):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )

    def set_offers(self, offers: list[Oferta], EAN: str, nazwa: str = ""):
        sorted_offers = sorted(
            offers,
            key=lambda oferta: oferta.cena_brutto,
        )

        # Usuń poprzednie dane, zachowując nagłówki.
        self.clearContents()
        self.setRowCount(len(sorted_offers))

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

            self.setCellWidget(
                row, 4, QuantityChanger(self.koszyk, EAN, oferta.hurtownia, nazwa)
            )

            self.resizeRowToContents(row)
