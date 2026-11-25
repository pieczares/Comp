import threading

from PySide6.QtCore import QObject, Signal

from integrations.Produkt_api import BladApi


class Worker(QObject):
    """Baza dla zadań wykonywanych w osobnym wątku.

    Podklasa nadpisuje metodę `zadanie()` (wykonywaną w wątku roboczym, bez dostępu
    do widgetów Qt). Wynik wraca sygnałami `done` / `failed` w wątku GUI.
    Sygnały niosą token, dzięki czemu strona może zignorować nieaktualne wyniki.
    Po `anuluj()` zadanie może się przerwać wcześniej, a sygnały nie są już emitowane.
    """

    done = Signal(int, object)
    failed = Signal(int, str)

    def __init__(self, token: int = 0, parent=None):
        super().__init__(parent)
        self._token = token
        self._anulowano = threading.Event()

    def zadanie(self):
        raise NotImplementedError

    def anuluj(self):
        self._anulowano.set()

    @property
    def anulowano(self) -> bool:
        return self._anulowano.is_set()

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            wynik = self.zadanie()
        except BladApi as e:
            if not self.anulowano:
                self._emit(self.failed, self._token, str(e))
        except Exception as e:
            if not self.anulowano:
                self._emit(self.failed, self._token, f"Nieoczekiwany błąd: {e}")
        else:
            if not self.anulowano:
                self._emit(self.done, self._token, wynik)

    @staticmethod
    def _emit(sygnal, *args):
        try:
            sygnal.emit(*args)
        except RuntimeError:
            # Obiekt Qt został już usunięty (np. zamknięcie aplikacji).
            pass
