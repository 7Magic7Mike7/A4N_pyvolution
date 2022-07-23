from abc import ABC, abstractmethod
from random import Random
from typing import Tuple

from arsfornons.simulation.world import World, Food, Creature
from arsfornons.util.config import Config
from arsfornons.util.navigation import Coordinate, Direction
from arsfornons.util.util_functions import hsv_to_rgb


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
    __EMPTY_WORLD_TRIPLE = 0, 0, 0

    def __init__(self, seed: int = 7):
        super().__init__()
        self.__rand = Random(seed)
        Creature.set_world_dimension(self._world.width, self._world.height)
        self.__plot_counter = 0
        self.__populate_counter = 0
        self.__coordinate = Coordinate(0, 0)   # for conversion to channel triple

    def process_step(self):
        self._world.update()

    def populate(self, data: str):
        self.__populate_counter += 1

        if self.__populate_counter % Config.instance().populate_calls_per_creature_spawn == 0:
            start_pos = Coordinate(
                self.__rand.randint(0, self._world.width - 1),
                self.__rand.randint(0, self._world.height - 1)  # todo base on data (not genome!)
            )
            creature = Creature.create(data, start_pos, Direction.North, world_width=self._world.width,
                                       world_height=self._world.height)
            self._world.place(creature)

        if Config.instance().populate_calls_per_food_spawn == 0:
            return  # special case for not spawning food
        if self.__populate_counter % Config.instance().populate_calls_per_food_spawn == 0:
            start_pos = Coordinate(
                self.__rand.randint(round(self._world.width * 0.25), round(self._world.width * 0.75)),
                self.__rand.randint(round(self._world.height * 0.25), round(self._world.height * 0.75)),
            )
            food = Food(start_pos)
            self._world.place(food)

    def __next_coordinate(self, pos: Coordinate = None):
        if pos is None:
            pos = self.__coordinate
        pos += Direction.Right
        if pos.x >= self._world.width:
            # we are at the end of the current row
            pos += Direction.Down
            if pos.y >= self._world.height:
                # we are also at the end of the world -> restart
                self.__coordinate = Coordinate(0, 0)
            else:
                self.__coordinate = Coordinate(0, pos.y)
        else:
            self.__coordinate = pos

    def to_channel_triple(self) -> Tuple[int, int, int]:
        # self._world.print()
        self.__plot_counter += 1
        self._world.plot(save=self.__plot_counter % Config.instance().steps_per_plot == 0)

        pos_tile = self._world.next_tile_after_or_at(self.__coordinate)
        if pos_tile is None:
            # world is empty
            self.__next_coordinate()
            return SimpleSimulation.__EMPTY_WORLD_TRIPLE

        pos, tile = pos_tile
        self.__next_coordinate(pos)
        return hsv_to_rgb(tile.color())
