import pickle
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from models.Koszyk import Koszyk
from models.Ulubione import Ulubione
from ui.MainWindow import MainWindow

STYLE_FILES = ("style.qss", "styles.qss")
KOSZYK = Path("koszyk.pkl")
ULUBIONE = Path("ulubione.pkl")

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

    base_dir = Path(__file__).resolve().parent
    app.setStyleSheet(
        "\n".join(
            (base_dir / name).read_text(encoding="utf-8") for name in STYLE_FILES
        )
    )


    koszyk = wczytaj(KOSZYK, Koszyk())
    ulubione = wczytaj(ULUBIONE, Ulubione())

    window = MainWindow(koszyk=koszyk, ulubione=ulubione)
    window.show()

    def przy_wyjsciu():
        zapisz(KOSZYK, koszyk)
        zapisz(ULUBIONE, ulubione)

    app.aboutToQuit.connect(przy_wyjsciu)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
