from abc import ABC, abstractmethod
from typing import Tuple


class Simulation(ABC):
    @abstractmethod
    def process_step(self):
        pass

    @abstractmethod
    def populate(self, data: Tuple[int, int, int]):
        pass

    @abstractmethod
    def to_channel_triple(self) -> Tuple[int, int, int]:
        pass


class SimpleSimulation(Simulation):

    def process_step(self):
        pass

    def populate(self, data: Tuple[int, int, int]):
        pass

    def to_channel_triple(self) -> Tuple[int, int, int]:
        pass
