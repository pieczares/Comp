from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from integrations.GeneratorPdf import GeneratorPdf
from models.Koszyk import Koszyk
from ui.CartTable import CartTable


class CartPage(QWidget):
    def __init__(self, go_to, koszyk: Koszyk):
        super().__init__()
        self.koszyk = koszyk

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Koszyk")
        title.setObjectName("PageTitle")

        self.error_label = QLabel()
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setTextFormat(Qt.TextFormat.PlainText)
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        self.empty_label = QLabel("Koszyk jest pusty.")

        self.generate_button = QPushButton("Generuj listę pdf")
        self.generate_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.generate_button.clicked.connect(self.generate_list)

        back_button = QPushButton("Wróć")
        back_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        back_button.clicked.connect(lambda: go_to("home"))

        self.tabela = CartTable(koszyk=self.koszyk, on_change=self._toggle_empty)

        layout.addWidget(title)
        layout.addWidget(self.error_label)
        layout.addWidget(self.tabela)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.generate_button)
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_cart()

    def _toggle_empty(self):
        is_empty = len(self.koszyk.get_oferty()) == 0
        self.empty_label.setVisible(is_empty)
        self.tabela.setVisible(not is_empty)
        self.generate_button.setVisible(not is_empty)

        blad = self.tabela.error_message
        if blad:
            self.error_label.setText(f"Nie udało się pobrać aktualnych cen: {blad}")
        self.error_label.setVisible(bool(blad))
        # Bez aktualnych cen (błąd lub trwające pobieranie) nie generujemy listy zakupów.
        self.generate_button.setEnabled(not blad and not self.tabela.loading)

    def update_cart(self):
        self.tabela.populate_table()
        self._toggle_empty()

    def generate_list(self):
        sciezka, _ = QFileDialog.getSaveFileName(self, "Zapisz listę zakupów", "lista_zakupow.pdf", "Pliki PDF (*.pdf)")
        if not sciezka:
            return
        if not sciezka.lower().endswith(".pdf"):
            sciezka += ".pdf"

        try:
            GeneratorPdf().generuj_pdf(koszyk=self.koszyk, sciezka=sciezka)
        except ValueError as e:
            QMessageBox.warning(self, "Lista zakupów", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Lista zakupów", f"Nie udało się zapisać PDF:\n{e}")
            return

        QMessageBox.information(self, "Lista zakupów", f"Lista zakupów została zapisana:\n{sciezka}")
