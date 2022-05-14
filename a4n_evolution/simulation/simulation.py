from abc import ABC, abstractmethod
from typing import Tuple

from a4n_evolution.simulation.world import World
from a4n_evolution.simulation.world.creatures import Creature
from util.navigation import Coordinate, Direction


class Simulation(ABC):
    __SIZE = 10

    def __init__(self):
        self.__world = World(Simulation.__SIZE)

    @property
    def _world(self) -> World:
        return self.__world

    @abstractmethod
    def process_step(self):
        pass

    @abstractmethod
    def populate(self, data: str):
        pass

    @abstractmethod
    def to_channel_triple(self) -> Tuple[int, int, int]:
        pass


class SimpleSimulation(Simulation):
    def process_step(self):
        for y in range(self._world.height):
            for x in range(self._world.width):
                tile = self._world.get(x=x, y=y)
                if tile:
                    tile.update(self._world.get)

    def populate(self, data: str):
        start_pos = Coordinate(int(self._world.width / 2), int(self._world.height / 2))
        creature = Creature(data, start_pos, Direction.North, self._world.width, self._world.height)
        creature.place(self._world)

    def to_channel_triple(self) -> Tuple[int, int, int]:
        self._world.print()
        return 0, 0, 0
