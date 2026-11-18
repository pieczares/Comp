from PySide6.QtWidgets import QMainWindow, QStackedWidget

from models.Koszyk import Koszyk
from models.Produkt import Produkt
from ui.HomePage import HomePage
from ui.OffersPage import OffersPage
from ui.CartPage import CartPage
from ui.FavoritesPage import FavoritesPage
from ui.ProductDetailsPage import ProductDetailsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.koszyk = Koszyk([])

        self.setWindowTitle("Sklep")
        self.resize(900, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = HomePage(self.go_to)
        self.offers_page = OffersPage(self.go_to)
        self.cart_page = CartPage(self.go_to, self.koszyk)
        self.favorites_page = FavoritesPage(self.go_to)
        self.product_details_page = ProductDetailsPage(self.go_to, self.koszyk)

        self.offers_page.product_selected.connect(self.show_product_details)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.offers_page)
        self.stack.addWidget(self.cart_page)
        self.stack.addWidget(self.favorites_page)
        self.stack.addWidget(self.product_details_page)

    #Przełączanie między stronami
    def go_to(self, page_name: str):
        pages = {
            "home": self.home_page,
            "offers": self.offers_page,
            "cart": self.cart_page,
            "favorites": self.favorites_page,
        }

        page = pages.get(page_name)
        if page_name == "cart":
            self.cart_page.update_cart()
        if page:
            self.stack.setCurrentWidget(page)

    #Otwarcie strony produktu, wywołanie z OffersPage, przekazanie obiektu Produkt do ProductDetailsPage
    def show_product_details(self, produkt: Produkt):
        self.product_details_page.set_product(produkt)
        self.stack.setCurrentWidget(self.product_details_page)
