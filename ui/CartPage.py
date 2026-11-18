from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

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

        back_button = QPushButton("Wróć do strony głównej")
        back_button.clicked.connect(lambda: go_to("home"))


        self.tabela = CartTable(koszyk=self.koszyk)

        layout.addWidget(title)
        layout.addWidget(self.tabela)
        layout.addWidget(self.empty_label)
        layout.addStretch()
        layout.addWidget(back_button)

    def update_cart(self):
        if len(self.koszyk.get_oferty()) == 0:
            self.empty_label.show()
            self.tabela.hide()
        else:
            self.empty_label.hide()
            self.tabela.show()
            # self.tabela.populate_table()
