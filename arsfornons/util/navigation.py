
from enum import Enum

from arsfornons.util import Logger


class Direction(Enum):
    Center = (0, 0)

    North = (0, -1)
    East = (1, 0)
    South = (0, 1)
    West = (-1, 0)
    N = North
    E = East
    S = South
    W = West

    Up = North
    Right = East
    Down = South
    Left = West
    U = Up
    R = Right
    D = Down
    L = Left

    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    @staticmethod
    def from_coordinates(c_from: "Coordinate", c_to: "Coordinate") -> "Direction":
        return direction(c_from, c_to)

    @staticmethod
    def values() -> "[Direction]":
        return [Direction.North, Direction.East, Direction.South, Direction.West]

    @staticmethod
    def to_float(direction: "Direction") -> float:
        length = len(Direction.values())
        value = 0   # Center (invalid)
        if direction.x == 0:
            if direction.y < 0:
                value = 1
            elif direction.y > 0:
                value = 3
        elif direction.y == 0:
            if direction.x > 0:
                value = 2
            elif direction.x < 0:
                value = 4
        return value / length

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    def is_horizontal(self) -> bool:
        """

        :return: True if direction is East or West, False otherwise
        """
        return self.x != 0

    def opposite(self) -> "Direction":
        if self == Direction.North:
            return Direction.South
        elif self == Direction.East:
            return Direction.West
        elif self == Direction.South:
            return Direction.North
        elif self == Direction.West:
            return Direction.East
        else:
            return Direction.Center

    def turn_right(self) -> "Direction":
        if self == Direction.North:
            return Direction.East
        elif self == Direction.East:
            return Direction.South
        elif self == Direction.South:
            return Direction.West
        elif self == Direction.West:
            return Direction.North
        else:
            return Direction.Center

    def turn_left(self) -> "Direction":
        if self == Direction.North:
            return Direction.West
        elif self == Direction.East:
            return Direction.North
        elif self == Direction.South:
            return Direction.East
        elif self == Direction.West:
            return Direction.South
        else:
            return Direction.Center

    def __add__(self, other) -> "Coordinate":
        if isinstance(other, Direction):
            return Coordinate(self.x + other.x, self.y + other.y)
        elif isinstance(other, Coordinate):
            return other + self
        else:
            Logger.instance().throw(NotImplementedError(f"Adding \"{other}\" to a Coordinate is not supported!"))

    def __mul__(self, other) -> "Coordinate":
        return Coordinate(0, 0) * other


class Coordinate:
    @staticmethod
    def distance(a: "Coordinate", b: "Coordinate") -> int:
        return abs(a.x - b.x) + abs(a.y - b.y)

    @staticmethod
    def is_before(a: "Coordinate", b: "Coordinate", row_wise: bool = True):
        """
        Compares if a is before b, meaning that it is encountered before b if we would go through all possible
        Coordinates either row- or column-wise.
        - Ex1: a = (0|1), b = (1|0), row_wise = True
               returns True because a.y < b.y
               if row_wise would be False, it would return False because b.x < a.x
        - Ex2: a = (7|0), b = (7|9), row_wise = True
               returns True because a and b are in the same row but a.x < b.x
        - Ex3: a = (9|9), b = (9|9), row_wise can either be True or False
               returns False because a == b and therefore a is not before b
        :param a: the first Coordinate for comparison
        :param b: the second Coordinate for comparison
        :param row_wise: whether rows or columns are the primary axis
        :return: True if a is encountered before b if we would go through all possible Coordinates
        """
        if a == b:
            return False

        if row_wise:
            return a.y < b.y or a.y == b.y and a.x < b.x
        else:
            return a.x < b.x or a.x == b.x and a.y < b.y

    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    def resolve(self) -> (int, int):
        return self.__x, self.__y

    def linearize(self, row_width: int) -> int:
        """
        Returns the index this Coordinate would have if it was stored in a row-wise fashion in a 1D array.

        :param row_width: width of one row of the grid stored in a corresponding 1D array
        :return:
        """
        return self.x + self.y * row_width

    def __add__(self, other) -> "Coordinate":
        if isinstance(other, Direction):
            return Coordinate(self.x + other.x, self.y + other.y)
        elif isinstance(other, Coordinate):
            return Coordinate(self.x + other.x, self.y + other.y)
        else:
            Logger.instance().throw(NotImplementedError(f"Adding \"{other}\" to a Coordinate is not supported!"))

    def __mul__(self, other) -> "Coordinate":
        if isinstance(other, float) or isinstance(other, int):
            return Coordinate(self.x * other, self.y * other)
        else:
            Logger.instance().throw(NotImplementedError(f"Multiplying \"{other}\" to a Coordinate is not supported!"))

    def __sub__(self, other) -> "Coordinate":
        if isinstance(other, Direction):
            return Coordinate(self.x - other.x, self.y - other.y)
        elif isinstance(other, Coordinate):
            return Coordinate(self.x - other.x, self.y - other.y)
        else:
            Logger.instance().throw(NotImplementedError(f"Subtracting \"{other}\" from a Coordinate is not supported!"))

    def __eq__(self, other) -> bool:
        if isinstance(other, Coordinate):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return 61 * self.x + 51 * self.y

    def __str__(self):
        return f"({self.__x}|{self.__y})"


def direction(c_from: Coordinate, c_to: Coordinate) -> Direction:
    diff = c_to - c_from
    if diff.x == 0 and diff.y == 0:
        return Direction.Center
    if abs(diff.x) > abs(diff.y):
        if diff.x > 0:
            return Direction.East
        else:
            return Direction.West
    else:
        if diff.y > 0:
            return Direction.South
        else:
            return Direction.North


def distance(a: Coordinate, b: Coordinate) -> int:
    diff_x = a.x - b.x
    diff_y = a.y - b.y
    if diff_x < 0:
        diff_x = -diff_x
    if diff_y < 0:
        diff_y = -diff_y
    return diff_x + diff_y
