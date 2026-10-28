from PySide6.QtWidgets import QMainWindow, QStackedWidget

from ui.HomePage import HomePage
from ui.OffersPage import OffersPage
from ui.CartPage import CartPage
from ui.FavoritesPage import FavoritesPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sklep")
        self.resize(900, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = HomePage(self.go_to)
        self.offers_page = OffersPage(self.go_to)
        self.cart_page = CartPage(self.go_to)
        self.favorites_page = FavoritesPage(self.go_to)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.offers_page)
        self.stack.addWidget(self.cart_page)
        self.stack.addWidget(self.favorites_page)

    def go_to(self, page_name: str):
        pages = {
            "home": self.home_page,
            "offers": self.offers_page,
            "cart": self.cart_page,
            "favorites": self.favorites_page,
        }

        page = pages.get(page_name)
        if page:
            self.stack.setCurrentWidget(page)