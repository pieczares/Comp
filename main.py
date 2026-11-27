import pickle
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from models.Alarmy import Alarmy
from models.Koszyk import Koszyk
from models.Ulubione import Ulubione
from ui.MainWindow import MainWindow

STYLE_FILE = "style.qss"
KOSZYK = Path("koszyk.pkl")
ULUBIONE = Path("ulubione.pkl")
ALARMY = Path("alarmy.pkl")

def wczytaj(plik: Path, domyslny):
    if plik.exists():
        with open(plik, "rb") as f:
            return pickle.load(f)
    return domyslny

def zapisz(plik:Path ,obj):
    with open(plik, "wb") as f:
        pickle.dump(obj, f)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    base_dir = Path(__file__).resolve().parent
    app.setStyleSheet((base_dir / STYLE_FILE).read_text(encoding="utf-8"))


    koszyk = wczytaj(KOSZYK, Koszyk())
    ulubione = wczytaj(ULUBIONE, Ulubione())
    alarmy = wczytaj(ALARMY, Alarmy())

    window = MainWindow(koszyk=koszyk, ulubione=ulubione, alarmy=alarmy)
    window.show()

    def przy_wyjsciu():
        zapisz(KOSZYK, koszyk)
        zapisz(ULUBIONE, ulubione)
        zapisz(ALARMY, alarmy)

    app.aboutToQuit.connect(przy_wyjsciu)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
