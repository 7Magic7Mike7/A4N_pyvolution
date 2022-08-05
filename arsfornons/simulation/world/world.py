import datetime
import os
from typing import Optional, Dict, Tuple

# from matplotlib import pyplot as plt

from arsfornons import Config
from arsfornons.simulation.world.tiles import Tile, Food
from arsfornons.simulation.world.creatures import Creature, Egg
from arsfornons.util.navigation import Coordinate
from arsfornons.util.util_functions import hsv_to_rgb


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
                return isinstance(t2, Food)  # eggs only win against food

            if isinstance(t1, Creature):
                if isinstance(t2, Food):
                    t1.eat(t2)
                elif isinstance(t2, Creature):
                    pass    # todo implement fighting?
                elif Config.instance().allow_egg_eating and isinstance(t2, Egg):
                    t1.eat(t2)
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
        self.__world: Dict[Coordinate, Tile] = {}

        # self.__fig, self.__ax = plt.subplots()
        self.__file_prefix = str(datetime.datetime.now()).replace(":", "_")
        self.__file_index = 0

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    def validate_position(self, c: Coordinate = None, x: int = None, y: int = None) -> Tuple[bool, Coordinate]:
        """
        Corrects the position in a sphere-like manner. E.g. if x is one space larger than width it will start back at 0.
        :param c:
        :param x:
        :param y:
        :return: True and c if c did not have to be adapted, False and a validated version of c otherwise
        """
        if c:
            x = c.x
            y = c.y
        elif x is None or y is None:
            raise RuntimeError("Not enough parameter provided to determine a position!")

        if 0 <= x < self.__width:
            if 0 <= y < self.__height:
                return True, Coordinate(x, y)
        return False, Coordinate(x % self.width, y % self.width)

    def get(self, c: Coordinate = None, x: int = None, y: int = None) -> Optional[Tile]:
        c = World.__coordinate(c, x, y)
        _, c = self.validate_position(c=c)
        if c in self.__world:
            return self.__world[c]
        return None

    def next_tile_after_or_at(self, start: Coordinate) -> Optional[Tuple[Coordinate, Tile]]:
        if start in self.__world:
            return start, self.__world[start]

        if len(self.__world.keys()) == 0:
            return None
        for key in self.__world.keys():
            if Coordinate.is_before(start, key, row_wise=True):
                # take the first tile after the start position
                return key, self.__world[key]
        # if no tiles are after start we restart searching at the beginning
        # recursion depth is guaranteed to be at most 1 because if there is no tile we return
        # and if there, is we'll find it
        return self.next_tile_after_or_at(Coordinate(0, 0))

    def place(self, tile: Tile):
        if self.validate_position(c=tile.pos)[0]:
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

        if self.__age % 100 == 0:
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
        pass
        # self.__ax.grid(True)
        """
        self.__ax.clear()
        self.__ax.set_xlim([-0.5, self.width + 0.5])
        self.__ax.set_ylim([-0.5, self.height + 0.5])

        for i, tile in enumerate(self.__world.values()):
            color = hsv_to_rgb(tile.color())
            color = f"#{'%02x%02x%02x' % (color[0], color[1], color[2])}"   # convert to hex color
            self.__ax.scatter(x=tile.pos.x, y=tile.pos.y, c=color)

        if save and Config.instance().save_plots:
            dir_path = os.path.join(World.__BASE_PATH, self.__file_prefix)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            path = os.path.join(dir_path, str(self.__file_index))
            self.__fig.savefig(path)
            self.__file_index += 1
        """