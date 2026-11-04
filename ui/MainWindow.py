from PySide6.QtWidgets import QMainWindow, QStackedWidget

from models.Produkt import Produkt
from ui.HomePage import HomePage
from ui.OffersPage import OffersPage
from ui.CartPage import CartPage
from ui.FavoritesPage import FavoritesPage
from ui.ProductDetailsPage import ProductDetailsPage


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
        self.product_details_page = ProductDetailsPage()

        self.offers_page.product_selected.connect(self.show_product_details)
        self.product_details_page.back_requested.connect(self.show_offers_page)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.offers_page)
        self.stack.addWidget(self.cart_page)
        self.stack.addWidget(self.favorites_page)
        self.stack.addWidget(self.product_details_page)

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

    def show_product_details(self, produkt: Produkt):
        self.product_details_page.set_product(produkt)
        self.stack.setCurrentWidget(self.product_details_page)

    def show_offers_page(self):
        self.stack.setCurrentWidget(self.offers_page)