"""Simulation of scattering a particle off another particle"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from .simulation import BaseSimulation  # type: ignore


class Simulation(BaseSimulation):
    def __init__(self):
        super().__init__("Scattering", 8)

        self.MOVING_PARTICLE_RADIUS = 3  # radius of the moving particle in m
        self.STATIC_PARTICLE_RADIUS = 4  # radius of the static particle in
        self.LAUNCH_SPEED = 10  # speed of the moving in m/s
        self.STATIC_PARTICLE_VELOCITY = 0  # speed of the static particle in m/s
        self.IMPACT_PARAMETER = 5  # impact parameter in m
        self.MOVING_PARTICLE_MASS = 1  # mass of the moving particle in kg
        self.STATIC_PARTICLE_MASS = 2  # mass of the static particle in kg

        self.state = np.zeros((1, self.state_length))  # x1, y1, x2, y2, vx1, vy1, vx2, vy2

    def initial_conditions(self):
        state = np.zeros(self.state_length)

        state[0] = -self.LAUNCH_SPEED * 3  # x position of the moving particle
        state[1] = self.IMPACT_PARAMETER  # y position of the moving particle
        state[2] = self.LAUNCH_SPEED  # x velocity of the moving particle
        state[3] = 0  # y velocity of the moving particle
        state[4] = 0  # x position of the static particle
        state[5] = 0  # y position of the static particle
        state[6] = 0  # x velocity of the static particle
        state[7] = 0  # y velocity of the static particle

        self.state[0] = state

        return state

    def axis_size(self):
        return max(self.LAUNCH_SPEED * 4, self.IMPACT_PARAMETER * 1.25)

    def simulate(self, initial_state):
        state = np.copy(initial_state)
        simulation = [np.copy(state)]

        for i in range(self.SIM_LENGTH * self.SIMS_PER_SECOND):
            state[0] += state[2] / self.SIMS_PER_SECOND
            state[1] += state[3] / self.SIMS_PER_SECOND
            state[2] = state[2]
            state[3] = state[3]

            state[4] += state[6] / self.SIMS_PER_SECOND
            state[5] += state[7] / self.SIMS_PER_SECOND
            state[6] = state[6]
            state[7] = state[7]

            if (
                np.sqrt((state[0] - state[4]) ** 2 + (state[1] - state[5]) ** 2)
                < self.MOVING_PARTICLE_RADIUS + self.STATIC_PARTICLE_RADIUS
            ):
                theta = np.arctan2(self.IMPACT_PARAMETER, self.MOVING_PARTICLE_RADIUS + self.STATIC_PARTICLE_RADIUS)
                state[2] = self.LAUNCH_SPEED * np.cos(theta)
                state[3] = self.LAUNCH_SPEED * np.sin(theta)

                state[6] = (self.MOVING_PARTICLE_MASS / self.STATIC_PARTICLE_MASS) * state[2]
                state[7] = -(self.MOVING_PARTICLE_MASS / self.STATIC_PARTICLE_MASS) * state[3]

            if (
                abs(state[0]) > self.axis_size()
                or abs(state[1]) > self.axis_size()
                or abs(state[4]) > self.axis_size()
                or abs(state[5]) > self.axis_size()
            ):
                break
            if i > self.MAX_SIMS:
                break

            simulation.append(np.copy(state))
            self.state = np.vstack([self.state, state])

        return np.array(simulation)

    def get_figure(self):
        simulation = self.simulate(self.initial_conditions())

        fig = plt.figure()

        ax = plt.gca()
        ax.set_xlim(-self.axis_size(), self.axis_size())
        ax.set_ylim(-self.axis_size(), self.axis_size())

        # Patches are used as they can be set to axis scale
        moving_particle = plt.Circle((self.state[0, 0], self.state[0, 1]), self.MOVING_PARTICLE_RADIUS)
        ax.add_patch(moving_particle)

        static_particle = plt.Circle((self.state[0, 4], self.state[0, 5]), self.STATIC_PARTICLE_RADIUS)
        ax.add_patch(static_particle)

        def animate_func(i):
            self.offset = i
            data = simulation[:, [0, 1]]
            moving_particle.center = (data[i, 0], data[i, 1])
            static_particle.center = (simulation[i, 4], simulation[i, 5])

            return moving_particle, static_particle

        anim = animation.FuncAnimation(
            fig, animate_func, frames=range(len(simulation)), interval=(1000 / self.SIMS_PER_SECOND)
        )

        ax.set_aspect("equal")

        return fig, anim

    def update_variables(self, variables) -> bool:
        self.state = np.zeros((1, self.state_length))
        if "r1" in variables:
            self.MOVING_PARTICLE_RADIUS = float(variables["r1"])
        if "r2" in variables:
            self.STATIC_PARTICLE_RADIUS = float(variables["r2"])
        if "b" in variables:
            self.IMPACT_PARAMETER = float(variables["b"])
        if "speed" in variables:
            self.LAUNCH_SPEED = float(variables["speed"])
        if "mass1" in variables:
            self.MOVING_PARTICLE_MASS = float(variables["mass1"])
        if "mass2" in variables:
            self.STATIC_PARTICLE_MASS = float(variables["mass2"])
        return True

    def get_fields(self) -> dict:
        fields = {
            "r1": {
                "type": "float",
                "value": self.MOVING_PARTICLE_RADIUS,
                "label": "Moving Particle Radius",
                "min": 0.001,
            },
            "r2": {
                "type": "float",
                "value": self.STATIC_PARTICLE_RADIUS,
                "label": "Static Particle Radius",
                "min": 0.001,
            },
            "b": {"type": "float", "value": self.IMPACT_PARAMETER, "label": "Impact Parameter", "min": 0},
            "speed": {"type": "float", "value": self.LAUNCH_SPEED, "label": "Launch Speed", "min": 1},
            "mass1": {
                "type": "float",
                "value": self.MOVING_PARTICLE_MASS,
                "label": "Moving Particle Mass",
                "min": 0.001,
            },
            "mass2": {
                "type": "float",
                "value": self.STATIC_PARTICLE_MASS,
                "label": "Static Particle Mass",
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
            "x1": {"label": "X Position of Moving Particle", "value": round(state[0], self.ROUND)},
            "y1": {"label": "Y Position of Moving Particle", "value": round(state[1], self.ROUND)},
            "vx1": {"label": "X Velocity of Moving Particle", "value": round(state[2], self.ROUND)},
            "vy1": {"label": "Y Velocity of Moving Particle", "value": round(state[3], self.ROUND)},
            "theta": {
                "label": "Angle of Scattering",
                "value": round(np.rad2deg(np.arctan2(state[3], state[2])), self.ROUND),
            },
            "x2": {"label": "X Position of Static Particle", "value": round(state[4], self.ROUND)},
            "y2": {"label": "Y Position of Static Particle", "value": round(state[5], self.ROUND)},
            "vx2": {"label": "X Velocity of Static Particle", "value": round(state[6], self.ROUND)},
            "vy2": {"label": "Y Velocity of Static Particle", "value": round(state[7], self.ROUND)},
        }

        return readings
