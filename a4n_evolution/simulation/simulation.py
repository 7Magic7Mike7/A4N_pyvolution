from abc import ABC, abstractmethod
from random import Random
from typing import Tuple

from a4n_evolution.simulation.world import World, Food, Creature
from util.config import Config
from util.navigation import Coordinate, Direction


class Simulation(ABC):
    __SIZE = Config.world_size()

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
    __STEPS_PER_PLOT = Config.steps_per_plot()

    def __init__(self, seed: int = 7):
        super().__init__()
        self.__rand = Random(seed)
        Creature.set_world_dimension(self._world.width, self._world.height)
        self.__plot_counter = 0
        self.__populate_counter = 0


    def process_step(self):
        self._world.update()

    def populate(self, data: str):
        self.__populate_counter += 1

        if self.__populate_counter % 2 == 0:
            start_pos = Coordinate(
                self.__rand.randint(0, self._world.width - 1),
                self.__rand.randint(0, self._world.height - 1)
            )
            creature = Creature.create(data, start_pos, Direction.North, world_width=self._world.width,
                                       world_height=self._world.height)
            self._world.place(creature)

        start_pos = Coordinate(
            self.__rand.randint(round(self._world.width * 0.25), round(self._world.width * 0.75)),
            self.__rand.randint(round(self._world.height * 0.25), round(self._world.height * 0.75)),
        )
        food = Food(start_pos)
        self._world.place(food)

    def to_channel_triple(self) -> Tuple[int, int, int]:
        # self._world.print()
        self.__plot_counter += 1
        self._world.plot(save=self.__plot_counter % SimpleSimulation.__STEPS_PER_PLOT == 0)
        return 0, 0, 0
