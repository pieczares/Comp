from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem, QTableWidget

from models.Oferta import Oferta


class OffersTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setColumnCount(4)
        self.setHorizontalHeaderLabels([
            "Hurtownia",
            "Cena netto",
            "Cena brutto",
            "Jednostka",
        ])

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers )

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()

        # Nazwa hurtowni zajmuje pozostałe dostępne miejsce.
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )

        for column in range(1, 4):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )

    def set_offers(self, offers: list[Oferta]):
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

            self.setItem(
                row, 3, QTableWidgetItem(oferta.jednostka)
            )