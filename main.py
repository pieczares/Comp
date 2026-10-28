import sys

from PySide6.QtWidgets import QApplication

from ui.MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    with open("styles.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()