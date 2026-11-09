import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ui.MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)

    style_path = Path(__file__).resolve().parent / "styles.qss"
    app.setStyleSheet(style_path.read_text(encoding="utf-8"))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()