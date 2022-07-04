from abc import ABC, abstractmethod
from random import Random
from typing import Tuple

from a4n_evolution.simulation.world import World, Food, Creature
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
    def __init__(self, seed: int = 7):
        super().__init__()
        self.__rand = Random(seed)
        Creature.set_world_dimension(self._world.width, self._world.height)

    def process_step(self):
        self._world.update()

    def populate(self, data: str):
        start_pos = Coordinate(
            self.__rand.randint(0, self._world.width - 1),
            self.__rand.randint(0, self._world.height - 1)
        )
        creature = Creature.create(data, start_pos, Direction.North)
        self._world.place(creature)

        start_pos = Coordinate(
            self.__rand.randint(0, self._world.width - 1),
            self.__rand.randint(0, self._world.height - 1)
        )
        food = Food(start_pos)
        self._world.place(food)

    def to_channel_triple(self) -> Tuple[int, int, int]:
        #self._world.print()
        self._world.plot()
        return 0, 0, 0
