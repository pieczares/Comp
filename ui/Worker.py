import threading

from PySide6.QtCore import QObject, Signal

from integrations.Produkt_api import BladApi


class Worker(QObject):
    """Wykonuje zadanie w osobnym wątku, a wynik zwraca sygnałami w wątku GUI.

    Sygnały niosą token, dzięki czemu strona może zignorować nieaktualne wyniki.
    Zadanie nie może dotykać widgetów Qt.
    """

    done = Signal(int, object)
    failed = Signal(int, str)

    def __init__(self, zadanie, token: int = 0, parent=None):
        super().__init__(parent)
        self._zadanie = zadanie
        self._token = token

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            wynik = self._zadanie()
        except BladApi as e:
            self._emit(self.failed, self._token, str(e))
        except Exception as e:
            self._emit(self.failed, self._token, f"Nieoczekiwany błąd: {e}")
        else:
            self._emit(self.done, self._token, wynik)

    @staticmethod
    def _emit(sygnal, *args):
        try:
            sygnal.emit(*args)
        except RuntimeError:
            # Obiekt Qt został już usunięty (np. zamknięcie aplikacji).
            pass
