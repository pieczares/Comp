from datetime import datetime
from decimal import Decimal
from html import escape

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QFont, QPageLayout, QPageSize, QPdfWriter, QTextDocument

from models.Koszyk import Koszyk
from models.ProduktWKoszyku import ProduktWKoszyku


class GeneratorPdf:

    def __kwota(self, wartosc: Decimal) -> str:
        return f"{wartosc:.2f} zł".replace(".", ",")

    def __grupuj(self, koszyk: Koszyk) -> tuple[dict[str, list[ProduktWKoszyku]], list[str]]:
        """Pobiera ceny i grupuje pozycje koszyka po hurtowniach.
        Zwraca (sekcje, pominięte pozycje, dla których nie udało się pobrać ceny)."""
        sekcje: dict[str, list[ProduktWKoszyku]] = {}
        pominiete: list[str] = []

        for oferta in koszyk.get_oferty():
            try:
                oferta.pobierz_ceny()
            except Exception as e:
                print(f"Błąd pobierania ceny {oferta.hurtownia}/{oferta.EAN}: {e}")
                pominiete.append(f"{oferta.nazwa or oferta.EAN} ({oferta.hurtownia})")
                continue
            sekcje.setdefault(oferta.hurtownia, []).append(oferta)

        return dict(sorted(sekcje.items())), pominiete

    def __zbuduj_html(self, sekcje: dict[str, list[ProduktWKoszyku]]) -> str:
        czesci = [
            "<h1>Lista zakupów</h1>",
            f"<p>Data: {datetime.now():%d.%m.%Y}</p>",
        ]

        for hurtownia, pozycje in sekcje.items():
            suma_netto = Decimal("0")
            suma_brutto = Decimal("0")

            czesci.append(f"<h2>{escape(hurtownia)}</h2>")
            czesci.append(
                '<table border="1" cellspacing="0" cellpadding="4" width="100%">'
            )
            czesci.append(
                '<tr bgcolor="#e6ecf7">'
                '<th width="15%" align="left">Kod</th>'
                '<th width="31%" align="left">Nazwa</th>'
                '<th width="11%" align="right">Cena netto</th>'
                '<th width="11%" align="right">Cena brutto</th>'
                '<th width="8%" align="right">Ilość</th>'
                '<th width="12%" align="right">Suma netto</th>'
                '<th width="12%" align="right">Suma brutto</th>'
                "</tr>"
            )

            for p in pozycje:
                wiersz_netto = p.cena_netto * p.ilosc
                wiersz_brutto = p.cena_brutto * p.ilosc
                suma_netto += wiersz_netto
                suma_brutto += wiersz_brutto
                czesci.append(
                    "<tr>"
                    f"<td>{escape(p.EAN)}</td>"
                    f"<td>{escape(p.nazwa or p.EAN)}</td>"
                    f'<td align="right">{self.__kwota(p.cena_netto)}</td>'
                    f'<td align="right">{self.__kwota(p.cena_brutto)}</td>'
                    f'<td align="right">{p.ilosc} {escape(p.jednostka)}</td>'
                    f'<td align="right">{self.__kwota(wiersz_netto)}</td>'
                    f'<td align="right">{self.__kwota(wiersz_brutto)}</td>'
                    "</tr>"
                )

            czesci.append("</table>")
            czesci.append(
                f"<p><b>Suma netto: {self.__kwota(suma_netto)}</b><br>"
                f"<b>Suma brutto: {self.__kwota(suma_brutto)}</b></p>"
            )

        return "\n".join(czesci)

    def generuj_pdf(self, koszyk: Koszyk, sciezka: str) -> list[str]:
        """Generuje PDF z zawartości koszyka. Zwraca listę pominiętych pozycji (bez ceny).
        Rzuca ValueError, gdy nie ma żadnej pozycji z ceną."""
        sekcje, pominiete = self.__grupuj(koszyk)
        if not sekcje:
            raise ValueError("Nie udało się pobrać cen żadnego produktu z koszyka.")

        writer = QPdfWriter(sciezka)
        writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        writer.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Unit.Millimeter)

        dokument = QTextDocument()
        dokument.setDefaultFont(QFont("Segoe UI", 9))
        dokument.setHtml(self.__zbuduj_html(sekcje))
        dokument.print_(writer)

        return pominiete
