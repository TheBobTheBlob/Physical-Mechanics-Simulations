from abc import ABC, abstractmethod


class BaseSimulation(ABC):
    def __init__(self, name: str, state_length: int):
        self.name = name
        self.offset = 0
        self.state_length = state_length

        self.SIM_LENGTH = 10000  # number of steps to simulate
        self.SIMS_PER_SECOND = 25

        self.ROUND = 5  # number of decimal places to round to
        self.MAX_SIMS = 50000  # maximum number of simulations to run

    @abstractmethod
    def initial_conditions(self):
        pass

    @abstractmethod
    def simulate(self, initial_state):
        pass

    @abstractmethod
    def get_figure(self):
        pass

    @abstractmethod
    def update_variables(self, variables) -> bool:
        pass

    @abstractmethod
    def get_fields(self) -> dict:
        pass

    @abstractmethod
    def get_readings(self) -> dict:
        pass
