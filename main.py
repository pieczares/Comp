import pickle
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from models.Koszyk import Koszyk
from models.Ulubione import Ulubione
from ui.MainWindow import MainWindow

STYLE_FILES = ("styles.qss", "style.qss")
KOSZYK = Path("koszyk.pkl")
ULUBIONE = Path("ulubione.pkl")

def wczytaj(PLIK: Path, domyslny):
    if PLIK.exists():
        with open(PLIK, "rb") as f:
            return pickle.load(f)
    return domyslny

def main():
    app = QApplication(sys.argv)

    base_dir = Path(__file__).resolve().parent
    app.setStyleSheet(
        "\n".join(
            (base_dir / name).read_text(encoding="utf-8") for name in STYLE_FILES
        )
    )


    koszyk = wczytaj(KOSZYK, Koszyk())
    lubione = wczytaj(ULUBIONE, Ulubione())

    window = MainWindow(koszyk=koszyk, ulubione=lubione)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
