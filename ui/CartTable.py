from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton

from integrations.Produkt_api import ProduktApi
from models.Koszyk import Koszyk
from models.Oferta import Oferta
from models.ProduktWKoszyku import ProduktWKoszyku


class CartTable(QTableWidget):
     def __init__(self, koszyk: Koszyk):
         super().__init__()
         self.koszyk = koszyk
         self.setColumnCount(5)
         self.setHorizontalHeaderLabels([
             "Hurtownia",
             "Cena netto",
             "Cena brutto",
             "Jednostka",
             "W koszyku",
         ])
         # self.populate_table()

     def populate_table(self):
         oferty = self.koszyk.get_oferty()
         self.clearContents()
         self.setRowCount(len(oferty))

         for row, oferta in enumerate(oferty):
             of = ProduktApi.pobierz_oferty_api(f"http://127.0.0.1:8000/produkty/oferta?hurtownia_id=1&kod={oferta.EAN}'")

             self.setItem(row, 0, QTableWidgetItem(oferta.hurtownia))
             self.setItem(row, 1, QTableWidgetItem(f"{of[0].cena_netto:.2f} zł"))
             self.setItem(row, 2, QTableWidgetItem(f"{of[0].cena_brutto:.2f} zł"))
             self.setItem(row, 3, QTableWidgetItem(of[0].jednostka))
             self.setItem(row, 4, QTableWidgetItem(str(oferta.ilosc)))

             remove_button = QPushButton("Usuń")
             remove_button.clicked.connect(lambda _, o=oferta: self.remove_offer(o))
             self.setCellWidget(row, 3, remove_button)

     def remove_offer(self, oferta: ProduktWKoszyku):
         self.koszyk.usun_oferte(oferta.EAN, oferta.hurtownia)
         self.populate_table()