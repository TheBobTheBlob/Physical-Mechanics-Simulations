"""Simulation of throwing a particle off of a slope"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation


class Simulation:
    def __init__(self):
        self.name = "Launching a Particle Off of a Slope"

        self.G_EARTH = 9.807  # acceleration due to gravity on Earth in m/s^2

        self.PARTICLE_MASS = 1  # mass of each particle in kg
        self.SLOPE_ANGLE = 30  # angle of the slope in degrees

        self.LAUNCH_ANGLE = 45  # angle of the launch in degrees
        self.LAUNCH_SPEED = 10  # speed of the launch in m/s

        self.state = np.zeros((1, 4))  # x, y, vx, vy
        self.mass = np.array([self.PARTICLE_MASS])  # mass of each particle. unit: kg

        # self.state[0] = self.initial_conditions()
        self.SIMULATION_LENGTH = 10000  # number of steps to simulate
        self.SIMULATIONS_PER_SECOND = 25

    def initial_conditions(self):
        # x, y, vx, vy
        state = np.zeros(4)

        state[0] = 0  # x position of the particle
        state[1] = 0  # y position of the particle
        state[2] = self.LAUNCH_SPEED * np.cos(np.deg2rad(self.LAUNCH_ANGLE))  # x velocity of the particle
        state[3] = self.LAUNCH_SPEED * np.sin(np.deg2rad(self.LAUNCH_ANGLE))  # y velocity of the particle

        self.state[0] = state

        return state

    def simulate(self, initial_state, steps, sims_per_sec):
        state = np.copy(initial_state)
        simulation = [np.copy(state)]

        for i in range(steps * sims_per_sec):
            state[0] += state[2] / sims_per_sec
            state[1] += state[3] / sims_per_sec
            state[2] = state[2]
            state[3] = initial_state[2] - (0.5 * self.G_EARTH * (i / sims_per_sec) ** 2)

            if state[1] < -np.tan(np.deg2rad(self.SLOPE_ANGLE)) * state[0]:
                break
            simulation.append(np.copy(state))

        return np.array(simulation)

    def get_figure(self):
        plt.close("all")
        simulation = self.simulate(
            self.initial_conditions(),
            self.SIMULATION_LENGTH,
            self.SIMULATIONS_PER_SECOND,
        )

        fig = plt.figure()
        scatter = plt.scatter(
            self.state[:, 0],
            self.state[:, 1],
        )

        line_x = np.linspace(simulation[-1, 0] * -0.1, simulation[-1, 0] * 1.1, 100)
        line_y = -np.tan(np.deg2rad(self.SLOPE_ANGLE)) * line_x

        plt.plot(line_x, line_y)
        plt.plot(simulation[:, 0], simulation[:, 1], visible=False)

        def animate_func(i):
            data = simulation[:, [0, 1]]
            scatter.set_offsets(data[i])
            return scatter

        anim = animation.FuncAnimation(
            fig, animate_func, frames=range(len(simulation)), interval=(1000 / self.SIMULATIONS_PER_SECOND)
        )

        plt.axis("scaled")

        return fig, anim

    def update_variables(self, variables):
        if "slope_angle" in variables:
            self.SLOPE_ANGLE = variables["slope_angle"]
        if "launch_angle" in variables:
            self.LAUNCH_ANGLE = variables["launch_angle"]
