import datetime
import os
from typing import Optional, Dict

from matplotlib import pyplot as plt

from a4n_evolution.simulation.world.tiles import Tile, Food
from a4n_evolution.simulation.world.creatures import Creature, Egg
from util.config import Config
from util.navigation import Coordinate
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

        if t2 is not None:
            if isinstance(t1, Egg):
                return isinstance(t2, Food) # eggs only win against food

            if isinstance(t1, Creature):
                if isinstance(t2, Food):
                    t1.eat(t2)
                elif isinstance(t2, Creature):
                    pass    # todo implement fighting?
                # todo eat eggs?
            elif isinstance(t1, Food):
                if isinstance(t2, Creature):
                    t2.eat(t1)

        return True     # by default the "new" one wins

    @staticmethod
    def __place(tile: Tile, world: Dict[Coordinate, "Tile"]):
        if tile is None:
            return
        if tile.pos in world:
            if World.__versus(tile, world[tile.pos]):
                world[tile.pos] = tile
        else:
            if World.__versus(tile, None):
                world[tile.pos] = tile

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
        self.__age = 0
        self.__world = {}

        self.__fig, self.__ax = plt.subplots()
        self.__file_prefix = str(datetime.datetime.now()).replace(":", "_")
        self.__file_index = 0

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

    def place(self, tile: Tile):
        if self.validate_position(c=tile.pos):
            World.__place(tile, self.__world)
        else:
            raise IndexError(f"{tile.pos} is not a valid position!")

    def update(self):
        self.__age += 1
        new_world = {}
        for tile in self.__world.values():
            if tile.update(self.get):
                World.__place(tile, new_world)
                World.__place(tile.produced(), new_world)   # this will place nothing if tile.produced() returns None
        self.__world = new_world

        if self.__age % 1000 == 999:
            print(f"Age of world = {self.__age}")

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

        if save and Config.save_data():
            dir_path = os.path.join(World.__BASE_PATH, self.__file_prefix)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            path = os.path.join(dir_path, str(self.__file_index))
            self.__fig.savefig(path)
            self.__file_index += 1
