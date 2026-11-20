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

        self.empty_label = QLabel("Koszyk jest pusty.")

        self.generate_button = QPushButton("Generuj listę")
        self.generate_button.clicked.connect(self.generate_list)

        back_button = QPushButton("Wróć do strony głównej")
        back_button.clicked.connect(lambda: go_to("home"))

        self.tabela = CartTable(koszyk=self.koszyk, on_change=self._toggle_empty)

        layout.addWidget(title)
        layout.addWidget(self.tabela)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.generate_button)
        layout.addStretch()
        layout.addWidget(back_button)

        self.update_cart()

    def _toggle_empty(self):
        is_empty = len(self.koszyk.get_oferty()) == 0
        self.empty_label.setVisible(is_empty)
        self.tabela.setVisible(not is_empty)
        self.generate_button.setVisible(not is_empty)

    def update_cart(self):
        self.tabela.populate_table()
        self._toggle_empty()

    def generate_list(self):
        sciezka, _ = QFileDialog.getSaveFileName(self, "Zapisz listę zakupów", "lista_zakupow.pdf", "Pliki PDF (*.pdf)")
        if not sciezka:
            return
        if not sciezka.lower().endswith(".pdf"):
            sciezka += ".pdf"

        sekcje, pominiete = self.tabela.pobierz_sekcje()
        if not sekcje:
            QMessageBox.warning(
                self, "Lista zakupów",
                "Nie udało się pobrać cen żadnego produktu, lista nie została wygenerowana.",
            )
            return

        try:
            GeneratorPdf().generuj_pdf(sekcje=sekcje, sciezka=sciezka)
        except Exception as e:
            QMessageBox.critical(self, "Lista zakupów", f"Nie udało się zapisać PDF:\n{e}")
            return

        tekst = f"Lista zakupów została zapisana:\n{sciezka}"
        if pominiete:
            tekst += "\n\nPominięto (brak ceny):\n" + "\n".join(pominiete)
        QMessageBox.information(self, "Lista zakupów", tekst)
