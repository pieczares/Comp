from decimal import Decimal

from models.Alarm import Alarm
from models.Produkt import Produkt


class Alarmy:
    alarmy: list[Alarm]

    def __init__(self):
        self.alarmy = []

    def znajdz(self, EAN: str) -> Alarm | None:
        for alarm in self.alarmy:
            if alarm.produkt.EAN == EAN:
                return alarm
        return None

    def ustaw(self, produkt: Produkt, cena: Decimal) -> Alarm:
        alarm = self.znajdz(produkt.EAN)
        if alarm is None:
            alarm = Alarm(produkt, cena)
            self.alarmy.append(alarm)
        else:
            alarm.zmien_cene(cena)
        return alarm

    def usun(self, EAN: str):
        self.alarmy = [a for a in self.alarmy if a.produkt.EAN != EAN]
