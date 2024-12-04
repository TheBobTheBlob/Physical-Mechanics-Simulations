from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

from gui.base import BaseWindow


class MainWindow(BaseWindow):
    def __init__(self, icon):
        super().__init__(icon)

        # Label
        label = QLabel("No simulations found")
        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)
