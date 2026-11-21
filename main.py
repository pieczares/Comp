import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ui.MainWindow import MainWindow

STYLE_FILES = ("styles.qss", "style.qss")


def main():
    app = QApplication(sys.argv)

    base_dir = Path(__file__).resolve().parent
    app.setStyleSheet(
        "\n".join(
            (base_dir / name).read_text(encoding="utf-8") for name in STYLE_FILES
        )
    )

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
