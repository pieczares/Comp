from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView, QHeaderView, QPushButton, QTableWidget, QTableWidgetItem,
    QWidget,
)

from loaders.PricesLoader import PricesLoader
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
        # Komunikat o pierwszym błędzie pobierania cen (None = wszystko w porządku).
        self.error_message: str | None = None
        # True, dopóki ceny są pobierane w tle.
        self.loading = False

        self._token = 0
        self._wiersze: list[ProduktWKoszyku] = []
        # (hurtownia, EAN) -> komunikat błędu dla pozycji, której ceny nie udało się pobrać.
        self._bledy: dict[tuple[str, str], str] = {}
        self._loader: PricesLoader | None = None

        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

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

    def _teksty_cen(self, oferta: ProduktWKoszyku) -> tuple[str, str, str]:
        # Pozycja, której ceny nie udało się pobrać, nie pokazuje nieaktualnej ceny.
        if (oferta.hurtownia, oferta.EAN) in self._bledy:
            return "—", "—", "—"
        # Ostatnio znane ceny (np. z poprzedniego pobrania) pokazujemy od razu.
        if oferta.jednostka:
            return (
                f"{oferta.cena_netto:.2f} zł",
                f"{oferta.cena_brutto:.2f} zł",
                oferta.jednostka,
            )
        if self.error_message:
            return "—", "—", "—"
        return "…", "…", "…"

    def _ustaw_ceny(self, row: int, netto: str, brutto: str, jednostka: str):
        right = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        netto_item = QTableWidgetItem(netto)
        brutto_item = QTableWidgetItem(brutto)
        netto_item.setTextAlignment(right)
        brutto_item.setTextAlignment(right)
        self.setItem(row, 2, netto_item)
        self.setItem(row, 3, brutto_item)
        self.setItem(row, 4, QTableWidgetItem(jednostka))

    def populate_table(self, odswiez_ceny: bool = True):
        """Buduje tabelę z koszyka.

        `odswiez_ceny=True` (wejście na stronę) pobiera aktualne ceny z serwera.
        `odswiez_ceny=False` (zmiana ilości, usunięcie pozycji) tylko przebudowuje wiersze
        z ostatnio znanych cen – bez zapytań sieciowych.
        """
        oferty = list(self.koszyk.get_oferty())
        self._wiersze = oferty

        if odswiez_ceny or not oferty:
            self._token += 1
            if self._loader is not None:
                self._loader.anuluj()
                self._loader = None
            self.error_message = None
            self._bledy = {}
            self.loading = bool(oferty)

        self.clearContents()
        self.setRowCount(len(oferty))

        qty_width = 170
        remove_width = 90

        for row, oferta in enumerate(oferty):
            self.setItem(row, 0, QTableWidgetItem(oferta.hurtownia))
            self.setItem(row, 1, QTableWidgetItem(oferta.nazwa or oferta.EAN))
            self._ustaw_ceny(row, *self._teksty_cen(oferta))

            changer = QuantityChanger(
                self.koszyk, oferta.EAN, oferta.hurtownia,
                oferta.nazwa, on_change=self._schedule_refresh,
            )
            w, _ = self._lock_min_size(changer)
            qty_width = max(qty_width, w + 8)
            self.setCellWidget(row, self.COL_QTY, changer)

            remove_button = QPushButton("Usuń")
            remove_button.setObjectName("QuantityButton")
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

        if odswiez_ceny and oferty:
            loader = PricesLoader(self._token, [(o.hurtownia, o.EAN) for o in oferty])
            loader.item.connect(self._on_cena)
            loader.done.connect(self._on_ceny_koniec)
            loader.failed.connect(self._on_ceny_blad)
            self._loader = loader
            loader.start()

    def _on_cena(self, token: int, hurtownia: str, ean: str, cena, blad):
        # Ceny spływają pozycja po pozycji; wiersze dopasowujemy po kluczu (hurtownia, EAN),
        # bo tabela mogła zostać przebudowana w trakcie pobierania.
        if token != self._token:
            return
        klucz = (hurtownia, ean)
        if cena is None:
            self._bledy[klucz] = blad or "Nieznany błąd."
        for row, oferta in enumerate(self._wiersze):
            if (oferta.hurtownia, oferta.EAN) != klucz:
                continue
            if cena is not None:
                oferta.cena_netto = cena.cena_netto
                oferta.cena_brutto = cena.cena_brutto
                oferta.jednostka = cena.jednostka
            self._ustaw_ceny(row, *self._teksty_cen(oferta))
        self._schedule_fit_rows()

    def _on_ceny_koniec(self, token: int, _wynik):
        if token != self._token:
            return
        # Błąd choćby jednej pozycji blokuje generowanie listy (CartPage czyta error_message),
        # ale pozostałe pozycje pokazują już aktualne ceny.
        self.error_message = next(iter(self._bledy.values()), None)
        self._po_pobraniu_cen()

    def _on_ceny_blad(self, token: int, message: str):
        if token != self._token:
            return
        for row in range(len(self._wiersze)):
            self._ustaw_ceny(row, "—", "—", "—")
        self.error_message = message
        self._po_pobraniu_cen()

    def _po_pobraniu_cen(self):
        self.loading = False
        self._schedule_fit_rows()
        if self.on_change:
            self.on_change()

    def _schedule_refresh(self):
        QTimer.singleShot(0, self._refresh)

    def _refresh(self):
        # Zmiana ilości / usunięcie pozycji nie zmienia cen – nie pytamy serwera ponownie.
        self.populate_table(odswiez_ceny=False)
        if self.on_change:
            self.on_change()

    def remove_offer(self, oferta: ProduktWKoszyku):
        self.koszyk.usun_oferte(oferta.EAN, oferta.hurtownia)
        self._schedule_refresh()
