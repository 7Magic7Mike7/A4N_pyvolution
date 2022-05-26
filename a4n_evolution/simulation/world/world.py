import datetime
import os
from typing import Optional

import matplotlib.colors
from matplotlib import pyplot as plt

from util.navigation import Coordinate
from a4n_evolution.simulation.world.tiles import Tile
from util.util_functions import hsv_to_rgb


class World:
    __BASE_PATH = os.path.join("data", "plots")

    @staticmethod
    def __versus(t1: Optional[Tile], t2: Optional[Tile]) -> bool:
        """
        Let's to tiles compete with each other (e.g. if they both won't to be located on the same position).
        :param t1:
        :param t2:
        :return: True if t1 wins, False if t2 wins
        """
        if t1 is None:
            return False
        return True     # currently always the "new" one wins

    @staticmethod
    def __coordinate(c: Optional[Coordinate], x: Optional[int], y: Optional[int]) -> Coordinate:
        if c is not None:
            return c
        if x is None or y is None:
            raise RuntimeError("Not enough parameter provided to determine a position!")
        return Coordinate(x, y)

    def __init__(self, size: int):
        self.__width = size
        self.__height = size
        self.__world = {}

        self.__fig, self.__ax = plt.subplots()
        self.__file_prefix = str(datetime.datetime.now()).replace(":", "_")
        self.__file_index = 0

        os.mkdir(os.path.join(World.__BASE_PATH, self.__file_prefix))

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    def validate_position(self, c: Coordinate = None, x: int = None, y: int = None) -> bool:
        if c:
            x = c.x
            y = c.y
        elif x is None or y is None:
            raise RuntimeError("Not enough parameter provided to determine a position!")

        if 0 <= x < self.__width:
            if 0 <= y < self.__height:
                return True
        return False

    def get(self, c: Coordinate = None, x: int = None, y: int = None) -> Optional[Tile]:
        c = World.__coordinate(c, x, y)
        if self.validate_position(c=c):
            if c in self.__world:
                return self.__world[c]
            return None
        else:
            raise IndexError(f"{c} is not a valid position!")

    def set(self, tile: Tile):
        if self.validate_position(c=tile.pos):
            if tile.pos in self.__world:
                if self.__versus(tile, self.__world[tile.pos]):
                    self.__world[tile.pos] = tile
            else:
                if self.__versus(tile, None):
                    self.__world[tile.pos] = tile
        else:
            raise IndexError(f"{tile.pos} is not a valid position!")

    def update(self):
        new_world = {}
        for tile in self.__world.values():
            if tile.update(self.get):
                new_world[tile.pos] = tile
        self.__world = new_world

    def print(self):
        str_rep = ""
        for y in range(self.__height):
            for x in range(self.__width):
                tile = self.get(x=x, y=y)
                if tile:
                    str_rep += tile.to_string()
                else:
                    str_rep += "_"
            str_rep += "\n"
        print(str_rep)

    def plot(self, save: bool = False):
        #self.__ax.grid(True)
        self.__ax.clear()
        self.__ax.set_xlim([-0.5, self.width + 0.5])
        self.__ax.set_ylim([-0.5, self.height + 0.5])

        for i, tile in enumerate(self.__world.values()):
            color = tile.color()
            color = hsv_to_rgb(color[0], color[1], color[2])
            color = f"#{'%02x%02x%02x' % (color[0], color[1], color[2])}"
            self.__ax.scatter(x=tile.pos.x, y=tile.pos.y, c=color)

        if save:
            path = os.path.join(World.__BASE_PATH, self.__file_prefix, str(self.__file_index))
            self.__fig.savefig(path)
            self.__file_index += 1
