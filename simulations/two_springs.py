"""Simulation of two objects connected by two springs"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from .simulation import BaseSimulation  # type: ignore


class Simulation(BaseSimulation):
    def __init__(self):
        super().__init__("Two Springs", 4)

        self.BOB_MASS = 1  # mass of the bob in kg
        self.SPRING_CONSTANT = 1  # spring constant of the string in N/m
        self.SPRING_LENGTH = 10  # length of the string in m

        self.state = np.zeros((1, self.state_length))  # y1, vy1, y2, vy2

    def initial_conditions(self):
        state = np.zeros(self.state_length)

        state[0] = self.SPRING_LENGTH  # y position of the top particle
        state[1] = 0  # y velocity of the top particle
        state[2] = self.SPRING_LENGTH * 2  # y position of the bottom particle
        state[3] = 0  # y velocity of the bottom particle

        self.state[0] = state

        return state

    def simulate(self, initial_state):
        state = np.copy(initial_state)
        simulation = [np.copy(state)]

        for i in range(self.SIM_LENGTH * self.SIMS_PER_SECOND):
            state[0] += state[1] / self.SIMS_PER_SECOND
            state[1] -= (
                -self.G_EARTH + (self.SPRING_CONSTANT / self.BOB_MASS) * (2 * state[0] - state[2])
            ) / self.SIMS_PER_SECOND
            state[2] += state[3] / self.SIMS_PER_SECOND
            state[3] -= (
                -self.G_EARTH - (self.SPRING_CONSTANT / self.BOB_MASS) * (state[0] - state[2] + self.SPRING_LENGTH)
            ) / self.SIMS_PER_SECOND

            if abs(state[0]) > self.SPRING_LENGTH * 10 or abs(state[2]) > self.SPRING_LENGTH * 10:
                break
            if i > self.MAX_SIMS:
                break

            simulation.append(np.copy(state))
            self.state = np.vstack([self.state, state])

        return np.array(simulation)

    def axis_size(self):
        return self.SPRING_LENGTH * 10

    def get_figure(self):
        simulation = self.simulate(self.initial_conditions())

        fig = plt.figure()
        top_bob = plt.scatter(0, self.state[0, 0], s=100, zorder=10)
        bottom_bob = plt.scatter(0, self.state[0, 2], s=100, zorder=10)

        ax = plt.gca()
        ax.set_xlim(-self.SPRING_LENGTH * 10, self.SPRING_LENGTH * 10)
        ax.set_ylim(np.max([np.max(simulation[:, 0]), np.max(simulation[:, 2])]), 0)

        # Spring lines
        (top_spring,) = ax.plot([], [], lw=1.5)
        (bottom_spring,) = ax.plot([], [], lw=1.5)

        def create_spring(start_y, end_y):
            spring_points = 100
            y_vals = np.linspace(start_y, end_y, spring_points)
            x_vals = np.sin(np.linspace(0, 2 * np.pi * 10, spring_points)) * 1
            return x_vals, y_vals

        def animate_func(i):
            self.offset = i

            top_bob.set_offsets([0, simulation[:, [0, 1]][i, 0]])
            bottom_bob.set_offsets([0, simulation[:, [2, 3]][i, 0]])

            top_spring.set_data(*create_spring(0, simulation[i, 0]))
            bottom_spring.set_data(*create_spring(simulation[i, 0], simulation[i, 2]))

            return top_bob, bottom_bob, top_spring, bottom_spring

        anim = animation.FuncAnimation(
            fig, animate_func, frames=range(len(simulation)), interval=(1000 / self.SIMS_PER_SECOND)
        )

        return fig, anim

    def update_variables(self, variables) -> bool:
        self.state = np.zeros((1, self.state_length))
        if "gravity" in variables:
            self.G_EARTH = float(variables["gravity"])
        if "spring_length" in variables:
            self.SPRING_LENGTH = float(variables["spring_length"])
        if "bob_mass" in variables:
            self.BOB_MASS = float(variables["bob_mass"])
        if "spring_constant" in variables:
            self.SPRING_CONSTANT = float(variables["spring_constant"])

        return True

    def get_fields(self) -> dict:
        fields = {
            "gravity": {"type": "float", "value": self.G_EARTH, "label": "Acceleration due to Gravity", "min": 1},
            "spring_length": {
                "type": "float",
                "value": self.SPRING_LENGTH,
                "label": "Length of String",
                "min": 1,
            },
            "bob_mass": {"type": "float", "value": self.BOB_MASS, "label": "Mass of Bob", "min": 0.001},
            "spring_constant": {
                "type": "float",
                "value": self.SPRING_CONSTANT,
                "label": "Spring Constant of String",
                "min": 0.001,
            },
        }

        return fields

    def get_readings(self) -> dict:
        try:
            state = self.state[self.offset]
        except IndexError:
            state = self.state[-1]

        readings = {
            "y1": {"label": "Y Position of Top Bob", "value": round(state[0], self.ROUND)},
            "vy1": {"label": "Y Velocity of Top Bob", "value": round(state[1], self.ROUND)},
            "y2": {"label": "Y Position of Bottom Bob", "value": round(state[2], self.ROUND)},
            "vy2": {"label": "Y Velocity of Bottom Bob", "value": round(state[3], self.ROUND)},
        }

        return readings
