from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSlider,
    QLabel,
)
from PySide6.QtCore import Qt, QTimer
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

        self.readings_layout = QVBoxLayout()

        self.refresh_canvas()

    def refresh_canvas(self):
        self.figure, self.anim = self.simulation.get_figure()
        self.canvas = FigureCanvas(self.figure)

    def click(self):
        self.refresh_canvas()
        self.action(self.position)

    def set_position(self, position):
        self.position = position

    def update_variables(self, variables) -> bool:
        success = self.simulation.update_variables(variables)

        if success:
            self.refresh_canvas()
            return True
        else:
            return False

    def edit_fields(self):
        layouts = []
        fields = {}
        labels = {}

        for field, data in self.simulation.get_fields().items():
            input_layout = QHBoxLayout()

            if data["type"] == "slider":
                fields[field] = QSlider(orientation=Qt.Horizontal)
                fields[field].setMinimum(data["min"])
                fields[field].setMaximum(data["max"])
                fields[field].setValue(data["value"])

                labels[field] = QLabel(f"{data["label"]}: {fields[field].value()}")

                def connect(field):
                    def inner():
                        self.update_simulation({field: fields[field].value()})

                    fields[field].sliderReleased.connect(inner)
                    fields[field].valueChanged.connect(
                        lambda: labels[field].setText(
                            f"{self.simulation.get_fields()[field]["label"]}: {fields[field].value()}"
                        )
                    )

                connect(field)
                input_layout.addWidget(labels[field])
                input_layout.addWidget(fields[field])

                layouts.append(input_layout)

        return layouts

    def readings(self):
        if self.readings_layout.count() != 0:
            return self.readings_layout

        for value in self.simulation.get_readings().values():
            self.readings_layout.addWidget(QLabel(f"{value["label"]}: {value["value"]}"))

        return self.readings_layout

    def update_readings(self):
        for i in range(self.readings_layout.count()):
            self.readings_layout.itemAt(i).widget().setText(
                f"{list(self.simulation.get_readings().values())[i]["label"]}: {list(self.simulation.get_readings().values())[i]["value"]}"
            )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Physical Mechanics Simulations")
        self.setMinimumSize(800, 600)

        main_layout = QHBoxLayout()
        simulation_layout = QVBoxLayout()
        experiment_list = QVBoxLayout()
        settings_list = QHBoxLayout()

        self.variable_list = QVBoxLayout()
        self.reading_widget = QWidget()
        self.reading_widget.setLayout(self.variable_list)
        self.reading_widget.setFixedWidth(200)

        self.graph_layout = QVBoxLayout()
        self.buttons = []
        self.graph_index = 0

        simulation_layout.addLayout(self.graph_layout)
        simulation_layout.addLayout(settings_list)

        main_layout.addLayout(experiment_list)
        main_layout.addLayout(simulation_layout)
        main_layout.addWidget(self.reading_widget)

        for index, file in enumerate(get_simulation_files()):
            button = SimulationButton(file.stem, self.change_figure, self.update_simulation)
            self.buttons.append(button)

            experiment_list.addWidget(button)

            if index == 0:
                self.graph_layout.addWidget(button.canvas)
                self.graph_index = index
                for field in button.edit_fields():
                    settings_list.addLayout(field)

                self.variable_list.addWidget(QLabel("Readings:"))
                self.variable_list.addLayout(button.readings())
                self.variable_list.addStretch()
                self.variable_timer = QTimer()
                self.variable_timer.timeout.connect(self.update_readings)
                self.variable_timer.start(10)

            button.set_position(index)

        widget = QWidget()
        widget.setLayout(main_layout)

        self.setCentralWidget(widget)

    def change_figure(self, position):
        self.graph_layout.removeWidget(self.buttons[self.graph_index].canvas)
        self.graph_index = position
        self.graph_layout.addWidget(self.buttons[self.graph_index].canvas)

    def update_simulation(self, variables):
        success = self.buttons[self.graph_index].update_variables(variables)

        if success:
            self.graph_layout.itemAt(self.graph_layout.count() - 1).widget().deleteLater()
            self.graph_layout.addWidget(self.buttons[self.graph_index].canvas)

    def update_readings(self):
        self.buttons[self.graph_index].update_readings()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
