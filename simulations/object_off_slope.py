"""Simulation of throwing an object off of a slope"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from .simulation import BaseSimulation  # type: ignore


class Simulation(BaseSimulation):
    def __init__(self):
        super().__init__("Launching an Object Off of a Slope", 4)

        self.PARTICLE_MASS = 10  # mass of the particle in kg
        self.SLOPE_ANGLE = 30  # angle of the slope in degrees
        self.LAUNCH_ANGLE = 45  # angle of the launch in degrees
        self.LAUNCH_SPEED = 10  # speed of the launch in m/s

        self.AIR_RESISTANCE = False  # whether or not to include air resistance in the simulation
        self.AIR_DENSITY = 1.225  # density of air in kg/m^3
        self.DRAG_COEFFICIENT = 0.47  # drag coefficient of a sphere

        self.state = np.zeros((1, self.state_length))  # x, y, vx, vy

    def initial_conditions(self):
        state = np.zeros(self.state_length)

        state[0] = 0  # x position of the particle
        state[1] = 0  # y position of the particle
        state[2] = self.LAUNCH_SPEED * np.cos(np.deg2rad(self.LAUNCH_ANGLE))  # x velocity of the particle
        state[3] = self.LAUNCH_SPEED * np.sin(np.deg2rad(self.LAUNCH_ANGLE))  # y velocity of the particle

        self.state[0] = state

        return state

    def simulate(self, initial_state):
        state = np.copy(initial_state)
        simulation = [np.copy(state)]

        for i in range(self.SIM_LENGTH * self.SIMS_PER_SECOND):
            if not self.AIR_RESISTANCE:
                state[0] += state[2] / self.SIMS_PER_SECOND
                state[1] += state[3] / self.SIMS_PER_SECOND
                state[2] = state[2]
                state[3] -= self.G_EARTH / self.SIMS_PER_SECOND
            else:
                state[0] += state[2] / self.SIMS_PER_SECOND
                state[1] += state[3] / self.SIMS_PER_SECOND
                state[2] -= (
                    (0.5 * self.AIR_DENSITY * self.DRAG_COEFFICIENT * state[2] * abs(state[2]))
                    / self.PARTICLE_MASS
                    / self.SIMS_PER_SECOND
                )
                state[3] -= (
                    self.G_EARTH
                    + ((0.5 * self.AIR_DENSITY * self.DRAG_COEFFICIENT * state[3] * abs(state[3])) / self.PARTICLE_MASS)
                ) / self.SIMS_PER_SECOND

            if state[1] < -np.tan(np.deg2rad(self.SLOPE_ANGLE)) * state[0]:
                break
            if i > self.MAX_SIMS:
                break

            simulation.append(np.copy(state))
            self.state = np.vstack([self.state, state])

        return np.array(simulation)

    def get_figure(self):
        simulation = self.simulate(self.initial_conditions())

        fig = plt.figure()
        scatter = plt.scatter(self.state[0, 0], self.state[0, 1], s=100)

        # Plots the slope
        line_x = np.linspace(simulation[-1, 0] * -0.1, simulation[-1, 0] * 1.1, 100)
        line_y = -np.tan(np.deg2rad(self.SLOPE_ANGLE)) * line_x
        plt.plot(line_x, line_y)

        # Plots an invisible line to set the axis limits
        plt.plot(simulation[:, 0], simulation[:, 1], visible=False)

        def animate_func(i):
            self.offset = i
            data = simulation[:, [0, 1]]
            scatter.set_offsets(data[i])
            return scatter

        anim = animation.FuncAnimation(
            fig, animate_func, frames=range(len(simulation)), interval=(1000 / self.SIMS_PER_SECOND)
        )

        plt.axis("scaled")

        return fig, anim

    def update_variables(self, variables) -> bool:
        self.state = np.zeros((1, self.state_length))
        if "slope_angle" in variables:
            self.SLOPE_ANGLE = int(variables["slope_angle"])
        if "launch_angle" in variables:
            self.LAUNCH_ANGLE = int(variables["launch_angle"])
        if "speed" in variables:
            self.LAUNCH_SPEED = float(variables["speed"])
        if "gravity" in variables:
            self.G_EARTH = float(variables["gravity"])
        if "mass" in variables:
            self.PARTICLE_MASS = float(variables["mass"])
        if "air_resistance" in variables:
            self.AIR_RESISTANCE = variables["air_resistance"]
        if "drag_coefficient" in variables:
            self.DRAG_COEFFICIENT = float(variables["drag_coefficient"])
        if "air_density" in variables:
            self.AIR_DENSITY = float(variables["air_density"])

        return True

    def get_fields(self) -> dict:
        fields = {
            "slope_angle": {"type": "slider", "min": 0, "max": 89, "value": self.SLOPE_ANGLE, "label": "Slope Angle"},
            "launch_angle": {
                "type": "slider",
                "min": 0,
                "max": 89,
                "value": self.LAUNCH_ANGLE,
                "label": "Launch Angle",
            },
            "speed": {"type": "float", "value": self.LAUNCH_SPEED, "label": "Launch Speed", "min": 1},
            "gravity": {"type": "float", "value": self.G_EARTH, "label": "Acceleration due to Gravity", "min": 1},
            "mass": {"type": "float", "value": self.PARTICLE_MASS, "label": "Particle Mass", "min": 1},
            "air_resistance": {"type": "checkbox", "value": self.AIR_RESISTANCE, "label": "Air Resistance"},
            "drag_coefficient": {
                "type": "float",
                "value": self.DRAG_COEFFICIENT,
                "label": "Drag Coefficient",
                "min": 0,
                "max": 1,
            },
            "air_density": {"type": "float", "value": self.AIR_DENSITY, "label": "Air Density", "min": 0.001},
        }

        return fields

    def get_readings(self) -> dict:
        try:
            state = self.state[self.offset]
        except IndexError:
            state = self.state[-1]

        readings = {
            "x": {"label": "X Position", "value": round(state[0], self.ROUND)},
            "y": {"label": "Y Position", "value": round(state[1], self.ROUND)},
            "vx": {"label": "X Velocity", "value": round(state[2], self.ROUND)},
            "vy": {"label": "Y Velocity", "value": round(state[3], self.ROUND)},
        }

        return readings
