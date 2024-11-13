from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
)
from PySide6.QtGui import QIntValidator
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import pathlib
import importlib

import matplotlib.pyplot

matplotlib.use("QtAgg")

# Makes the graphs dark mode
matplotlib.pyplot.style.use("dark_background")


def get_simulation_files():
    files = pathlib.Path("simulations").rglob("*.py")

    return [file for file in files]


class SimulationButton(QPushButton):
    def __init__(self, text, action, update_simulation):
        module = importlib.import_module(f"simulations.{text}")
        self.simulation = module.Simulation()

        super().__init__(self.simulation.name)
        self.clicked.connect(self.click)

        self.action = action
        self.update_simulation = update_simulation

        self.figure = None
        self.anim = None
        self.position = None
        self.canvas = None

        self.refresh_canvas()

    def refresh_canvas(self):
        self.figure, self.anim = self.simulation.get_figure()
        self.canvas = FigureCanvas(self.figure)

    def click(self):
        self.refresh_canvas()
        self.action(self.position)

    def set_position(self, position):
        self.position = position

    def update_variables(self, variables):
        self.simulation.update_variables(variables)
        self.refresh_canvas()

    def edit_fields(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Physical Mechanics Simulations")
        self.setMinimumSize(800, 600)

        main_layout = QHBoxLayout()
        simulation_layout = QVBoxLayout()
        experiment_list = QVBoxLayout()
        variable_list = QVBoxLayout()
        settings_list = QHBoxLayout()

        input_edit = QLineEdit()
        input_edit.setValidator(QIntValidator())
        input_edit.textChanged.connect(self.update_simulation)
        settings_list.addWidget(input_edit)

        self.graph_layout = QVBoxLayout()
        self.buttons = []
        self.graph_index = 0

        simulation_layout.addLayout(self.graph_layout)
        simulation_layout.addLayout(settings_list)

        main_layout.addLayout(experiment_list)
        main_layout.addLayout(simulation_layout)
        main_layout.addLayout(variable_list)

        for index, file in enumerate(get_simulation_files()):
            button = SimulationButton(file.stem, self.change_figure, self.update_simulation)
            self.buttons.append(button)

            experiment_list.addWidget(button)

            if index == 0:
                self.graph_layout.addWidget(button.canvas)
                self.graph_index = index
            button.set_position(index)

        widget = QWidget()
        widget.setLayout(main_layout)

        self.setCentralWidget(widget)

    def change_figure(self, position):
        self.graph_layout.removeWidget(self.buttons[self.graph_index].canvas)
        self.graph_index = position
        self.graph_layout.addWidget(self.buttons[self.graph_index].canvas)

    def update_simulation(self):
        self.graph_layout.removeWidget(self.buttons[self.graph_index].canvas)

        self.buttons[self.graph_index].update_variables({"slope_angle": 80})

        self.graph_layout.removeWidget(self.buttons[self.graph_index].canvas)
        self.graph_layout.addWidget(self.buttons[self.graph_index].canvas)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
