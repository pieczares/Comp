from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from html import escape

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QFont, QPageLayout, QPageSize, QPdfWriter, QTextDocument


@dataclass
class PozycjaListy:
    kod: str
    nazwa: str
    cena_netto: Decimal
    cena_brutto: Decimal
    ilosc: int
    jednostka: str


def _kwota(wartosc: Decimal) -> str:
    return f"{wartosc:.2f} zł".replace(".", ",")


def _zbuduj_html(sekcje: dict[str, list[PozycjaListy]]) -> str:
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
                f"<td>{escape(p.kod)}</td>"
                f"<td>{escape(p.nazwa)}</td>"
                f'<td align="right">{_kwota(p.cena_netto)}</td>'
                f'<td align="right">{_kwota(p.cena_brutto)}</td>'
                f'<td align="right">{p.ilosc} {escape(p.jednostka)}</td>'
                f'<td align="right">{_kwota(wiersz_netto)}</td>'
                f'<td align="right">{_kwota(wiersz_brutto)}</td>'
                "</tr>"
            )

        czesci.append("</table>")
        czesci.append(
            f"<p><b>Suma netto: {_kwota(suma_netto)}</b><br>"
            f"<b>Suma brutto: {_kwota(suma_brutto)}</b></p>"
        )

    return "\n".join(czesci)


def generuj_pdf(sekcje: dict[str, list[PozycjaListy]], sciezka: str) -> None:
    writer = QPdfWriter(sciezka)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Unit.Millimeter)

    dokument = QTextDocument()
    dokument.setDefaultFont(QFont("Segoe UI", 9))
    dokument.setHtml(_zbuduj_html(sekcje))
    dokument.print_(writer)
