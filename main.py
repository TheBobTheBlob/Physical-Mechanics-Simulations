import gui.main_window as main_window
from PySide6.QtWidgets import QApplication
import sys
import pathlib
import gui.no_simulations as no_simulations


def get_simulation_files():
    if getattr(sys, "frozen", False):  # If running in a PyInstaller bundle
        base_path = pathlib.Path(sys._MEIPASS)  # Temp directory where PyInstaller unpacks
    else:
        base_path = pathlib.Path(__file__).parent
    files = pathlib.Path(base_path / "simulations").rglob("*.py")

    # simulation.py contains the base class for all simulations so we don't want to include it in the list of simulations
    return [file for file in files if file.stem != "simulation"]


def get_icon_file():
    if getattr(sys, "frozen", False):  # If running in a PyInstaller bundle
        base_path = pathlib.Path(sys._MEIPASS)  # Temp directory where PyInstaller unpacks
    else:
        base_path = pathlib.Path(__file__).parent
    return base_path / "icon.png"


if __name__ == "__main__":
    simulations = get_simulation_files()
    app = QApplication(sys.argv)

    if len(simulations) == 0:
        window = no_simulations.MainWindow(get_icon_file())
    else:
        window = main_window.MainWindow(get_icon_file(), simulations)

    window.show()
    app.exec()
