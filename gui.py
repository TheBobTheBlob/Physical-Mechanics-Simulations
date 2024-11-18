from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSlider,
    QLabel,
    QLineEdit,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIntValidator, QDoubleValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import importlib

import matplotlib.pyplot

matplotlib.use("QtAgg")
matplotlib.pyplot.style.use("dark_background")  # Dark theme
# BUG: Still dark if user theme is light


class SimulationButton(QPushButton):
    def __init__(self, text, action, update_simulation):
        module = importlib.import_module(f"simulations.{text}")
        self.simulation = module.Simulation()

        super().__init__(self.simulation.name)
        self.clicked.connect(self.click)

        self.setStyleSheet("padding: 10px;")

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
            input_layout = QVBoxLayout()

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

            elif data["type"] == "integer":
                only_int = QIntValidator()

                if "min" in data:
                    only_int.setBottom(data["min"])
                if "max" in data:
                    only_int.setTop(data["max"])

                fields[field] = QLineEdit()
                fields[field].setValidator(only_int)
                fields[field].setText(str(data["value"]))

                labels[field] = QLabel(f"{data["label"]}:")

                def connect(field):
                    def inner():
                        if fields[field].text() != "" and int(fields[field].text()) >= data["min"]:
                            self.update_simulation({field: int(fields[field].text())})

                    fields[field].textChanged.connect(inner)

                connect(field)
                input_layout.addWidget(labels[field])
                input_layout.addWidget(fields[field])

            elif data["type"] == "float":
                only_float = QDoubleValidator()

                if "min" in data:
                    only_float.setBottom(data["min"])
                if "max" in data:
                    only_float.setTop(data["max"])

                fields[field] = QLineEdit()
                fields[field].setValidator(only_float)
                fields[field].setText(str(data["value"]))

                labels[field] = QLabel(f"{data["label"]}:")

                def connect(field):
                    def inner():
                        if fields[field].text() not in ["", "."] and float(fields[field].text()) >= data["min"]:
                            self.update_simulation({field: float(fields[field].text())})

                    fields[field].textChanged.connect(inner)

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


class Heading(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin-top: 10px; margin-bottom: 10px; margin-left: -5px;"
        )


class MainWindow(QMainWindow):
    def __init__(self, simulations: list):
        super().__init__()
        self.setWindowTitle("Physical Mechanics Simulations")
        self.setMinimumSize(800, 600)
        self.showMaximized()

        # Layouts
        main_layout = QHBoxLayout()

        buttons_widget = QWidget()
        buttons_list = QVBoxLayout()
        buttons_list.addWidget(Heading("Simulations"))
        buttons_widget.setLayout(buttons_list)
        buttons_widget.setMaximumWidth(300)

        self.settings_list = QVBoxLayout()
        self.readings_list = QVBoxLayout()

        # Sidebar
        sidebar = QVBoxLayout()
        sidebar_widget = QWidget()

        sidebar.addWidget(Heading("Settings"))
        sidebar.addLayout(self.settings_list)
        sidebar.addLayout(self.readings_list)
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setMaximumWidth(300)

        self.graph_layout = QVBoxLayout()
        self.buttons = []
        self.graph_index = 0

        main_layout.addWidget(buttons_widget)
        main_layout.addLayout(self.graph_layout)
        main_layout.addWidget(sidebar_widget)

        # Add simulation buttons

        for index, file in enumerate(simulations):
            button = SimulationButton(file.stem, self.change_figure, self.update_simulation)
            self.buttons.append(button)

            buttons_list.addWidget(button)

            if index == 0:
                self.graph_layout.addWidget(button.canvas)
                self.graph_index = index

                for field in button.edit_fields():
                    self.settings_list.addLayout(field)

                self.readings_list.addWidget(Heading("Readings"))
                self.readings_list.addLayout(button.readings())
                self.readings_list.addStretch()
                self.variable_timer = QTimer()
                self.variable_timer.timeout.connect(self.update_readings)
                self.variable_timer.start(10)

            button.set_position(index)

        buttons_list.addStretch()

        # Set up the main widget

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
