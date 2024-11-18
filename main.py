from gui import MainWindow
from PySide6.QtWidgets import QApplication
import sys
import pathlib


def get_simulation_files():
    files = pathlib.Path("simulations").rglob("*.py")

    # simulation.py contains the base class for all simulations so we don't want to include it in the list of simulations
    return [file for file in files if file.stem != "simulation"]


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow(get_simulation_files())
    window.show()

    app.exec()
