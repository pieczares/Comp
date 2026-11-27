from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QInputDialog, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from loaders.OffersLoader import OffersLoader
from models.Alarm import Alarm
from models.Alarmy import Alarmy


class AlarmsPage(QWidget):
    def __init__(self, go_to, alarmy: Alarmy):
        super().__init__()
        self.alarmy = alarmy
        self._token = 0
        self._loader: OffersLoader | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Alarmy cenowe")
        title.setObjectName("PageTitle")

        self.empty_label = QLabel(
            "Nie masz alarmów cenowych. Ustaw je na stronie Ulubione."
        )

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
        self._render()
        self._load_offers()

    def _load_offers(self):
        self._token += 1
        if self._loader is not None:
            self._loader.anuluj()
            self._loader = None
        eans = [a.produkt.EAN for a in self.alarmy.alarmy]
        if not eans:
            return
        loader = OffersLoader(self._token, eans)
        loader.item.connect(self._on_offers)
        self._loader = loader
        loader.start()

    def _on_offers(self, token: int, ean: str, oferty, blad):
        if token != self._token:
            return
        alarm = self.alarmy.znajdz(ean)
        if alarm is None:
            return
        if oferty is None:
            alarm.produkt.set_offers_error(blad or "Nieznany błąd.")
        else:
            alarm.produkt.set_offers(oferty)
        self._render()

    def _render(self):
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.deleteLater()

        alarmy = list(self.alarmy.alarmy)
        self.empty_label.setVisible(not alarmy)
        self.scroll.setVisible(bool(alarmy))

        for alarm in alarmy:
            self.items_layout.addWidget(self._create_item(alarm))
        self.items_layout.addStretch()

    def _create_item(self, alarm: Alarm) -> QFrame:
        produkt = alarm.produkt
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        name = QLabel(produkt.name)
        name.setObjectName("ProductName")
        name.setWordWrap(True)
        name.setTextFormat(Qt.TextFormat.PlainText)

        ean = QLabel(f"Kod: {produkt.EAN}")
        ean.setTextFormat(Qt.TextFormat.PlainText)

        target = QLabel(f"Cena docelowa (brutto): {alarm.cena:.2f} zł")

        najnizsza = produkt.lowest_price()
        if najnizsza is None:
            aktualna = "Aktualna najniższa cena: brak danych"
        else:
            aktualna = (
                f"Aktualna najniższa cena: {najnizsza.cena_brutto:.2f} zł "
                f"({najnizsza.hurtownia})"
            )
        current = QLabel(aktualna)
        current.setTextFormat(Qt.TextFormat.PlainText)

        if not alarm.aktywny:
            status_text = "Alarm wyłączony"
        elif alarm.czy_spelniony():
            status_text = "Cena osiągnięta!"
        else:
            status_text = "Alarm aktywny, czekam na spadek ceny"
        status = QLabel(status_text)

        buttons = QHBoxLayout()
        change = QPushButton("Zmień cenę")
        toggle = QPushButton("Wyłącz" if alarm.aktywny else "Włącz")
        remove = QPushButton("Usuń")
        change.clicked.connect(lambda: self._change_price(alarm))
        toggle.clicked.connect(lambda: self._toggle(alarm))
        remove.clicked.connect(lambda: self._remove(alarm))
        buttons.addStretch()
        buttons.addWidget(change)
        buttons.addWidget(toggle)
        buttons.addWidget(remove)

        for w in (name, ean, target, current, status):
            layout.addWidget(w)
        layout.addLayout(buttons)
        return frame

    def _change_price(self, alarm: Alarm):
        cena, ok = QInputDialog.getDouble(
            self, "Zmień cenę alarmu", "Nowa cena docelowa brutto (zł):",
            float(alarm.cena), 0.01, 1_000_000.0, 2,
        )
        if ok:
            alarm.zmien_cene(Decimal(str(cena)))
            self._render()

    def _toggle(self, alarm: Alarm):
        alarm.zmien_aktywnosc()
        self._render()

    def _remove(self, alarm: Alarm):
        self.alarmy.usun(alarm.produkt.EAN)
        self._render()
