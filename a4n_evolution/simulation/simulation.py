from abc import ABC, abstractmethod
from random import Random
from typing import Tuple

from a4n_evolution.simulation.world import World, Food, Creature
from util.config import Config
from util.navigation import Coordinate, Direction
from util.util_functions import hsv_to_rgb


class Simulation(ABC):
    def __init__(self):
        self.__world = World(Config.instance().world_size)

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
        self.__plot_counter = 0
        self.__populate_counter = 0
        self.__x, self.__y = 0, 0   # for conversion to channel triple

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
        self._world.plot(save=self.__plot_counter % Config.instance().steps_per_plot == 0)

        tile = self._world.get(x=self.__x, y=self.__y)
        self.__x += 1
        if self.__x >= self._world.width:
            self.__x = 0
            self.__y += 1
            if self.__y >= self._world.height:
                self.__y = 0

        if tile is None:
            return 0, 0, 0
        else:
            return hsv_to_rgb(tile.color())
