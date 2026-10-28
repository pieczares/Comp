from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from models.Produkt import Produkt


class ProductCard(QFrame):
    def __init__(self, produkt: Produkt, parent=None):
        super().__init__(parent)

        self.produkt = produkt

        self.setObjectName("ProductCard")
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        self.name_label = QLabel()
        self.name_label.setObjectName("ProductName")
        self.name_label.setWordWrap(True)

        prices_layout = QHBoxLayout()
        prices_layout.setSpacing(20)

        self.cena_netto = QLabel()
        self.cena_brutto = QLabel()

        self.cena_netto.setObjectName("ProductPrice")
        self.cena_brutto.setObjectName("ProductPrice")

        prices_layout.addWidget(self.cena_netto)
        prices_layout.addWidget(self.cena_brutto)
        prices_layout.addStretch()

        layout.addWidget(self.name_label)
        layout.addLayout(prices_layout)

        self.refresh()

    def refresh(self):
        oferta = self.produkt.lowest_price()

        self.name_label.setText(self.produkt.name)

        if oferta is None:
            self.cena_netto.setText("Brak dostępnych ofert")
            self.cena_brutto.setText("")
            return

        jednostka = oferta.jednostka

        self.cena_netto.setText(
            f"Netto: {self._format_price(oferta.cena_netto)} zł / {jednostka}"
        )
        self.cena_brutto.setText(
            f"Brutto: {self._format_price(oferta.cena_brutto)} zł / {jednostka}"
        )

    @staticmethod
    def _format_price(value) -> str:
        try:
            return f"{float(value):.2f}"
        except (TypeError, ValueError):
            return "—"