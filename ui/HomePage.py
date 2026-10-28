from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Tile(QFrame):
    def __init__(self, title: str, subtitle: str, on_click):
        super().__init__()

        self.setObjectName("Tile")
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("TileTitle")
        title_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("TileSubtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        self.mousePressEvent = lambda event: on_click()


class HomePage(QWidget):
    def __init__(self, go_to):
        super().__init__()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(40, 40, 40, 40)
        root_layout.setSpacing(30)

        header = QLabel("Witaj w sklepie")
        header.setObjectName("PageTitle")
        header.setAlignment(Qt.AlignCenter)

        tiles_layout = QGridLayout()
        tiles_layout.setSpacing(25)

        tiles_layout.addWidget(
            Tile("Przeglądaj ofertę", "Zobacz dostępne produkty", lambda: go_to("offers")),
            0, 0,
        )
        tiles_layout.addWidget(
            Tile("Koszyk", "Sprawdź wybrane produkty", lambda: go_to("cart")),
            0, 1,
        )
        tiles_layout.addWidget(
            Tile("Ulubione", "Twoje zapisane produkty", lambda: go_to("favorites")),
            0, 2,
        )

        buttons_layout = QHBoxLayout()
        back_button = QPushButton("Wróć")
        back_button.clicked.connect(lambda: go_to("home"))
        buttons_layout.addWidget(back_button)
        buttons_layout.addStretch()

        root_layout.addWidget(header)
        root_layout.addLayout(tiles_layout)
        root_layout.addStretch()
        root_layout.addLayout(buttons_layout)