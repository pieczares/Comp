import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from models.Product import Product

# PRODUCTS = [
#     Product(
#         "Smartfon Nova X",
#         "Smartfony",
#         "📱",
#         [("TechMarket", 1899.00), ("Elektronix", 1999.00), ("SmartShop", 1949.00)],
#     ),
#     Product(
#         "Laptop Horizon 14",
#         "Laptopy",
#         "💻",
#         [("TechMarket", 3299.00), ("Komputerowo", 3499.00), ("Elektronix", 3399.00)],
#     ),
#     Product(
#         "Słuchawki AirSound Pro",
#         "Audio",
#         "🎧",
#         [("AudioPlanet", 449.00), ("TechMarket", 499.00), ("SmartShop", 479.00)],
#     ),
#     Product(
#         'Monitor Vision 27"',
#         "Monitory",
#         "🖥️",
#         [("Komputerowo", 899.00), ("Elektronix", 999.00), ("TechMarket", 949.00)],
#     ),
#     Product(
#         "Głośnik SoundBox Mini",
#         "Audio",
#         "🔊",
#         [("AudioPlanet", 199.00), ("SmartShop", 229.00), ("Elektronix", 219.00)],
#     ),
#     Product(
#         "Smartfon Nova Lite",
#         "Smartfony",
#         "📱",
#         [("SmartShop", 999.00), ("TechMarket", 1099.00), ("Elektronix", 1049.00)],
#     ),
# ]
#
#
# def money(value: float) -> str:
#     return f"{value:,.2f}".replace(",", " ").replace(".", ",") + " zł"
#
#
#
# class OffersDialog(QDialog):
#     def __init__(self, product: Product, parent=None):
#         super().__init__(parent)
#
#         self.setWindowTitle("Porównanie ofert")
#         self.setMinimumWidth(480)
#
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(24, 24, 24, 24)
#         layout.setSpacing(14)
#
#         title = QLabel(product.name)
#         title.setObjectName("SectionTitle")
#         title.setWordWrap(True)
#         layout.addWidget(title)
#
#         description = QLabel("Przykładowe oferty • bez kosztów dostawy")
#         description.setObjectName("Muted")
#         layout.addWidget(description)
#
#         offers = sorted(product.offers, key=lambda offer: offer[1])
#
#         for index, (shop, price) in enumerate(offers):
#             row = QFrame()
#             row.setObjectName("Offer")
#             row_layout = QHBoxLayout(row)
#             row_layout.setContentsMargins(14, 14, 14, 14)
#
#             shop_label = QLabel(shop)
#             row_layout.addWidget(shop_label)
#
#             if index == 0:
#                 badge = QLabel("Najtaniej")
#                 badge.setObjectName("Badge")
#                 row_layout.addWidget(badge)
#
#             row_layout.addStretch()
#
#             price_label = QLabel(money(price))
#             price_label.setStyleSheet("font-size: 18px; font-weight: 700;")
#             row_layout.addWidget(price_label)
#
#             layout.addWidget(row)
#
#         close_button = QPushButton("Zamknij")
#         close_button.clicked.connect(self.accept)
#         layout.addWidget(close_button)
#
#
# class ProductCard(QFrame):
#     def __init__(self, product: Product, parent=None):
#         super().__init__(parent)
#         self.product = product
#         self.setObjectName("ProductCard")
#         self.setMinimumWidth(240)
#         self.setSizePolicy(
#             QSizePolicy.Policy.Expanding,
#             QSizePolicy.Policy.Preferred,
#         )
#
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(18, 18, 18, 18)
#         layout.setSpacing(10)
#
#         image = QLabel(product.symbol)
#         image.setObjectName("ProductImage")
#         image.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         image.setFixedHeight(120)
#         layout.addWidget(image)
#
#         category = QLabel(product.category)
#         category.setObjectName("Muted")
#         layout.addWidget(category)
#
#         title = QLabel(product.name)
#         title.setObjectName("ProductTitle")
#         title.setWordWrap(True)
#         title.setMinimumHeight(46)
#         layout.addWidget(title)
#
#         hint = QLabel("Najniższa cena")
#         hint.setObjectName("Muted")
#         layout.addWidget(hint)
#
#         price = QLabel(money(product.lowest_price))
#         price.setObjectName("Price")
#         layout.addWidget(price)
#
#         shops = QLabel(f"Porównaj oferty w {len(product.offers)} sklepach")
#         shops.setObjectName("Muted")
#         layout.addWidget(shops)
#
#         layout.addStretch()
#
#         compare_button = QPushButton("Porównaj ceny")
#         compare_button.clicked.connect(self.show_offers)
#         layout.addWidget(compare_button)
#
#     def show_offers(self):
#         dialog = OffersDialog(self.product, self)
#         dialog.exec()
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.setWindowTitle("CenaRadar — porównywarka cen")
#         self.resize(1150, 820)
#         self.setMinimumSize(620, 600)
#
#         self.filtered_products = []
#         self.column_count = 0
#
#         root = QWidget()
#         root.setObjectName("Root")
#         self.setCentralWidget(root)
#
#         root_layout = QVBoxLayout(root)
#         root_layout.setContentsMargins(0, 0, 0, 0)
#         root_layout.setSpacing(0)
#
#         # Nagłówek
#         header = QFrame()
#         header.setObjectName("Header")
#         header_layout = QHBoxLayout(header)
#         header_layout.setContentsMargins(30, 18, 30, 18)
#
#         logo = QLabel("CenaRadar")
#         logo.setObjectName("Logo")
#         header_layout.addWidget(logo)
#         header_layout.addStretch()
#
#         tagline = QLabel("Porównuj. Wybieraj. Oszczędzaj.")
#         tagline.setObjectName("Muted")
#         header_layout.addWidget(tagline)
#
#         root_layout.addWidget(header)
#
#         # Przewijana zawartość strony
#         self.scroll = QScrollArea()
#         self.scroll.setWidgetResizable(True)
#         self.scroll.setHorizontalScrollBarPolicy(
#             Qt.ScrollBarPolicy.ScrollBarAlwaysOff
#         )
#
#         content = QWidget()
#         content_layout = QVBoxLayout(content)
#         content_layout.setContentsMargins(30, 26, 30, 24)
#         content_layout.setSpacing(24)
#
#         self.scroll.setWidget(content)
#         root_layout.addWidget(self.scroll)
#
#         # Sekcja powitalna
#         hero = QFrame()
#         hero.setObjectName("Hero")
#         hero_layout = QVBoxLayout(hero)
#         hero_layout.setContentsMargins(28, 26, 28, 26)
#         hero_layout.setSpacing(14)
#
#         hero_title = QLabel("Znajdź produkt.\nNie przepłacaj.")
#         hero_title.setObjectName("HeroTitle")
#         hero_layout.addWidget(hero_title)
#
#         hero_description = QLabel(
#             "Porównaj ceny elektroniki i wybierz najkorzystniejszą ofertę."
#         )
#         hero_description.setObjectName("HeroDescription")
#         hero_description.setWordWrap(True)
#         hero_layout.addWidget(hero_description)
#
#         search_layout = QHBoxLayout()
#         search_layout.setSpacing(12)
#
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText(
#             "Szukaj produktu, np. laptop, słuchawki..."
#         )
#         self.search_input.setClearButtonEnabled(True)
#         search_layout.addWidget(self.search_input, 1)
#
#         search_button = QPushButton("Szukaj")
#         search_button.clicked.connect(self.apply_filters)
#         search_layout.addWidget(search_button)
#
#         hero_layout.addLayout(search_layout)
#         content_layout.addWidget(hero)
#
#         # Filtry
#         filters = QHBoxLayout()
#         filters.setSpacing(12)
#
#         self.category_combo = QComboBox()
#         self.category_combo.addItems(
#             ["Wszystkie kategorie"]
#             + sorted({product.category for product in PRODUCTS})
#         )
#         filters.addWidget(self.category_combo)
#
#         self.sort_combo = QComboBox()
#         self.sort_combo.addItems([
#             "Polecane",
#             "Cena: od najniższej",
#             "Cena: od najwyższej",
#             "Nazwa: A–Z",
#         ])
#         filters.addWidget(self.sort_combo)
#
#         filters.addStretch()
#
#         reset_button = QPushButton("Wyczyść")
#         reset_button.setObjectName("Secondary")
#         reset_button.clicked.connect(self.reset_filters)
#         filters.addWidget(reset_button)
#
#         content_layout.addLayout(filters)
#
#         section_layout = QHBoxLayout()
#
#         section_title = QLabel("Odkryj produkty")
#         section_title.setObjectName("SectionTitle")
#         section_layout.addWidget(section_title)
#         section_layout.addStretch()
#
#         self.results_label = QLabel()
#         self.results_label.setObjectName("Muted")
#         section_layout.addWidget(self.results_label)
#
#         content_layout.addLayout(section_layout)
#
#         # Siatka produktów
#         self.products_widget = QWidget()
#         self.grid = QGridLayout(self.products_widget)
#         self.grid.setContentsMargins(0, 0, 0, 0)
#         self.grid.setSpacing(18)
#         content_layout.addWidget(self.products_widget)
#
#         self.empty_label = QLabel(
#             "Nie znaleziono produktów.\nZmień frazę lub kategorię."
#         )
#         self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.empty_label.setObjectName("Muted")
#         self.empty_label.setMinimumHeight(120)
#         content_layout.addWidget(self.empty_label)
#
#         footer = QLabel(
#             "Wersja demonstracyjna • dane i ceny są fikcyjne"
#         )
#         footer.setObjectName("Muted")
#         footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
#
#         content_layout.addStretch()
#         content_layout.addWidget(footer)
#
#         self.search_input.textChanged.connect(self.apply_filters)
#         self.search_input.returnPressed.connect(self.apply_filters)
#         self.category_combo.currentTextChanged.connect(self.apply_filters)
#         self.sort_combo.currentTextChanged.connect(self.apply_filters)
#
#         self.apply_filters()
#
#     def apply_filters(self):
#         query = self.search_input.text().strip().casefold()
#         category = self.category_combo.currentText()
#
#         products = [
#             product
#             for product in PRODUCTS
#             if (
#                 not query
#                 or query in f"{product.name} {product.category}".casefold()
#             )
#             and (
#                 category == "Wszystkie kategorie"
#                 or product.category == category
#             )
#         ]
#
#         sorting = self.sort_combo.currentIndex()
#
#         if sorting == 1:
#             products.sort(key=lambda product: product.lowest_price)
#         elif sorting == 2:
#             products.sort(
#                 key=lambda product: product.lowest_price,
#                 reverse=True,
#             )
#         elif sorting == 3:
#             products.sort(key=lambda product: product.name.casefold())
#
#         self.filtered_products = products
#         self.results_label.setText(f"Wyniki: {len(products)}")
#         self.empty_label.setVisible(not products)
#         self.products_widget.setVisible(bool(products))
#
#         self.rebuild_grid()
#
#     def reset_filters(self):
#         self.search_input.clear()
#         self.category_combo.setCurrentIndex(0)
#         self.sort_combo.setCurrentIndex(0)
#
#     def calculate_columns(self):
#         available_width = self.scroll.viewport().width() - 60
#         return max(1, min(4, (available_width + 18) // 258))
#
#     def rebuild_grid(self):
#         while self.grid.count():
#             item = self.grid.takeAt(0)
#             widget = item.widget()
#             if widget is not None:
#                 widget.hide()
#                 widget.deleteLater()
#
#         # Usuń rozciąganie kolumn po poprzednim układzie.
#         for column in range(4):
#             self.grid.setColumnStretch(column, 0)
#
#         self.column_count = self.calculate_columns()
#
#         for index, product in enumerate(self.filtered_products):
#             row, column = divmod(index, self.column_count)
#             self.grid.addWidget(ProductCard(product), row, column)
#
#         for column in range(self.column_count):
#             self.grid.setColumnStretch(column, 1)
#
#     def resizeEvent(self, event):
#         super().resizeEvent(event)
#
#         if hasattr(self, "grid"):
#             if self.calculate_columns() != self.column_count:
#                 self.rebuild_grid()
#
                
                
                
from integrations.produkty_api import pobierz_produkty_api

if __name__ == "__main__":

    produkty: list[Product] = pobierz_produkty_api("http://127.0.0.1:8000/produkty?limit=200&offset=0")

    for produkt in produkty:
        print(
            produkt.lowest_price()
        )

    # app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    #
    # style_path = Path(__file__).resolve().parent / "styles.qss"
    # app.setStyleSheet(style_path.read_text(encoding="utf-8"))
    #
    # window = MainWindow()
    # window.show()
    #
    # sys.exit(app.exec())