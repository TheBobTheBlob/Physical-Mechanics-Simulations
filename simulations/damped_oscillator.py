"""Simulation of a damped oscillator"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from .simulation import BaseSimulation  # type: ignore


class Simulation(BaseSimulation):
    def __init__(self):
        super().__init__("Damped Oscillator")

        self.G_EARTH = 9.807  # acceleration due to gravity on Earth in m/s^2

        self.BOB_MASS = 10  # mass of the bob in kg
        self.DAMPING_CONSTANT = 0.2  # damping constant in Ns/m
        self.START_ANGLE = 85  # angle of the intial sendoff in degrees
        self.STRING_LENGTH = 1  # length of the string in meters

        self.state = np.zeros((1, 2))  # theta, omega
        self.mass = np.array([self.BOB_MASS])  # mass of each particle. unit: kg

    def initial_conditions(self):
        state = np.zeros(2)  # theta, omega

        state[0] = np.deg2rad(self.START_ANGLE)  # angle of the bob
        state[1] = 0  # angular velocity of the bob

        self.state[0] = state

        return state

    def simulate(self, initial_state):
        state = np.copy(initial_state)
        simulation = [np.copy(state)]

        for i in range(self.SIM_LENGTH * self.SIMS_PER_SECOND):
            state[1] += ((-self.DAMPING_CONSTANT * state[1]) / (self.BOB_MASS * self.STRING_LENGTH**2)) - (
                (self.G_EARTH * np.sin(state[0])) / self.STRING_LENGTH
            ) / self.SIMS_PER_SECOND
            state[0] += state[1] / self.SIMS_PER_SECOND

            if abs(state[1]) < 0.001 and abs(state[0]) < 0.001:
                break
            if i > self.MAX_SIMS:
                break

            simulation.append(np.copy(state))
            self.state = np.vstack([self.state, state])

        return np.array(simulation)

    def get_figure(self):
        simulation = self.simulate(self.initial_conditions())

        fig = plt.figure()
        (line,) = plt.plot([], [], lw=2)
        (dot,) = plt.plot([], [], "o")

        ax = fig.gca()

        ax.set_xlim(-self.STRING_LENGTH * 1.25, self.STRING_LENGTH * 1.25)
        ax.set_ylim(-self.STRING_LENGTH * 1.25, self.STRING_LENGTH * 0.5)

        def animate_func(i):
            self.offset = i
            data = simulation[:, [0, 1]]
            x = self.STRING_LENGTH * np.sin(data[i, 0])
            y = -self.STRING_LENGTH * np.cos(data[i, 0])

            line.set_data([0, x], [0, y])
            dot.set_data([x], [y])

            return line

        anim = animation.FuncAnimation(
            fig, animate_func, frames=range(len(simulation)), interval=(1000 / self.SIMS_PER_SECOND)
        )

        plt.axis("scaled")

        return fig, anim

    def update_variables(self, variables) -> bool:
        self.state = np.zeros((1, 2))
        if "start_angle" in variables:
            self.START_ANGLE = int(variables["start_angle"])
        if "damping" in variables:
            self.DAMPING_CONSTANT = float(variables["damping"])
        if "length" in variables:
            self.STRING_LENGTH = float(variables["length"])
        if "gravity" in variables:
            self.G_EARTH = float(variables["gravity"])
        if "mass" in variables:
            self.BOB_MASS = float(variables["mass"])

        return True

    def get_fields(self) -> dict:
        fields = {
            "start_angle": {
                "type": "slider",
                "min": 0,
                "max": 89,
                "value": self.START_ANGLE,
                "label": "Starting Angle",
            },
            "damping": {"type": "float", "value": self.DAMPING_CONSTANT, "label": "Damping Constant", "min": 0.0001},
            "length": {"type": "float", "value": self.STRING_LENGTH, "label": "String length", "min": 0.0001},
            "gravity": {"type": "float", "value": self.G_EARTH, "label": "Acceleration due to Gravity", "min": 1},
            "mass": {"type": "float", "value": self.BOB_MASS, "label": "Bob Mass", "min": 0.0001},
        }

        return fields

    def get_readings(self) -> dict:
        try:
            state = self.state[self.offset]
        except IndexError:
            state = self.state[-1]

        readings = {
            "theta": {"label": "Angular Position", "value": round(np.rad2deg(state[0]), self.ROUND)},
            "omega": {"label": "Angular Velocity", "value": round(state[1], self.ROUND)},
        }

        return readings
