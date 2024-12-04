from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIcon
from pathlib import Path


class BaseWindow(QMainWindow):
    def __init__(self, icon_path: Path):
        super().__init__()
        self.setWindowTitle("Physical Mechanics Simulations")
        self.setMinimumSize(800, 600)

        icon = QIcon(str(icon_path))
        self.setWindowIcon(icon)
