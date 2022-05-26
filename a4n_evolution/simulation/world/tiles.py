from abc import ABC, abstractmethod
from typing import Callable, Optional, Tuple

from util.navigation import Coordinate


class Tile(ABC):
    __NEXT_ID = 1

    def __init__(self, pos: Coordinate):
        self._pos = pos
        self.__id = Tile.__NEXT_ID
        Tile.__NEXT_ID += 1

    @property
    def tid(self) -> int:
        return self.__id

    @property
    def pos(self) -> Coordinate:
        return self._pos

    def color(self) -> Tuple[float, float, float]:
        """

        :return: HSV color, all parts in [0, 1]
        """
        return 0, 0, 0  # black

    @abstractmethod
    def update(self, get_tile: Callable[[Optional[Coordinate], Optional[int], Optional[int]], Optional["Tile"]]) \
            -> bool:
        """

        :param get_tile:
        :return: True if the Tile is still alive, False if it "died" in this update
        """
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass

    def __str__(self) -> str:
        return self.to_string()
