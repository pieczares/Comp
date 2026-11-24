from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QHBoxLayout, QVBoxLayout


class ProductPlaceholder(QFrame):
    """Pulsujący szkielet karty produktu pokazywany w trakcie ładowania."""

    # (wysokość paska, udział szerokości w %)
    BARS = ((18, 70), (14, 45), (14, 40))

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProductPlaceholder")
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        for height, width_percent in self.BARS:
            bar = QFrame()
            bar.setObjectName("PlaceholderBar")
            bar.setFixedHeight(height)

            row = QHBoxLayout()
            row.addWidget(bar, width_percent)
            row.addStretch(100 - width_percent)
            layout.addLayout(row)

        layout.addStretch()

        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        self._animation = QPropertyAnimation(effect, b"opacity", self)
        self._animation.setDuration(1200)
        self._animation.setStartValue(1.0)
        self._animation.setKeyValueAt(0.5, 0.4)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._animation.setLoopCount(-1)
        self._animation.start()
