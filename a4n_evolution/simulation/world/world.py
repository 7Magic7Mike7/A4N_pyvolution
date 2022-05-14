from typing import Optional, Iterable, List

from util.navigation import Coordinate
from a4n_evolution.simulation.world.tiles import Tile


class World:
    def __init__(self, size: int):
        self.__width = size
        self.__height = size
        self.__grid = [[None] * self.__width for _ in range(self.__height)]  # stores tiles

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
        if c:
            x = c.x
            y = c.y
        elif x is None or y is None:
            raise RuntimeError("Not enough parameter provided to determine a position!")

        if self.validate_position(x=x, y=y):
            return self.__grid[y][x]
        else:
            raise IndexError(f"{c} is not a valid position!")

    def get_neighbors(self, c: Coordinate, perception_range: int = 1) -> List[List[Tile]]:
        neighbors = [[]]
        for r in range(perception_range):
            pass
        return neighbors

    def set(self, tile: Tile):
        if self.validate_position(c=tile.pos):
            self.__grid[tile.pos.y][tile.pos.x] = tile
        else:
            raise IndexError(f"{tile.pos} is not a valid position!")

    def reset(self, c: Coordinate = None, x: int = None, y: int = None):
        if c:
            x = c.x
            y = c.y
        elif x is None or y is None:
            raise RuntimeError("Not enough parameter provided to determine a position!")

        if self.validate_position(x=x, y=y):
            self.__grid[y][x] = None
        else:
            raise IndexError(f"{c} is not a valid position!")

    def __iter__(self) -> Iterable[Iterable[Optional[Tile]]]:
        return self.__grid

    def print(self):
        str_rep = ""
        for row in self.__grid:
            for tile in row:
                if tile:
                    str_rep += tile.to_string()
                else:
                    str_rep += "_"
            str_rep += "\n"
        print(str_rep)
