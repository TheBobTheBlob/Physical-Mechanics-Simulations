from abc import ABC, abstractmethod


class BaseSimulation(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def initial_conditions(self):
        pass

    @abstractmethod
    def simulate(self, initial_state, steps, sims_per_sec):
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
