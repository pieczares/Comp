from decimal import Decimal

from PySide6.QtWidgets import QInputDialog, QPushButton

from models.Alarmy import Alarmy
from models.Produkt import Produkt


class AlarmButton(QPushButton):
    def __init__(self, alarmy: Alarmy, produkt: Produkt):
        super().__init__()
        self.alarmy = alarmy
        self.produkt = produkt
        self.clicked.connect(self._ustaw_alarm)
        self._odswiez()

    def _odswiez(self):
        alarm = self.alarmy.znajdz(self.produkt.EAN)
        if alarm is None:
            self.setText("Ustaw alarm cenowy")
        else:
            self.setText(f"Alarm: {alarm.cena:.2f} zł")

    def _ustaw_alarm(self):
        alarm = self.alarmy.znajdz(self.produkt.EAN)
        start = float(alarm.cena) if alarm else 0.0
        if start == 0.0:
            oferta = self.produkt.lowest_price()
            if oferta is not None:
                start = float(oferta.cena_brutto)
        cena, ok = QInputDialog.getDouble(
            self,
            "Alarm cenowy",
            f"Powiadom, gdy cena brutto spadnie do (zł):\n{self.produkt.name}",
            start, 0.01, 1_000_000.0, 2,
        )
        if ok:
            self.alarmy.ustaw(self.produkt, Decimal(str(cena)))
            self._odswiez()
