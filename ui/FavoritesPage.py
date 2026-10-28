from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class FavoritesPage(QWidget):
    def __init__(self, go_to):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Ulubione")
        title.setObjectName("PageTitle")

        empty_label = QLabel("Nie masz jeszcze ulubionych produktów.")

        back_button = QPushButton("Wróć do strony głównej")
        back_button.clicked.connect(lambda: go_to("home"))

        layout.addWidget(title)
        layout.addWidget(empty_label)
        layout.addStretch()
        layout.addWidget(back_button)