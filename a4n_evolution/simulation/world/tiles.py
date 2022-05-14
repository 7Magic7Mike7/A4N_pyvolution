from abc import ABC, abstractmethod
from typing import Callable, Optional

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

    @abstractmethod
    def update(self, get_tile: Callable[[Optional[Coordinate], Optional[int], Optional[int]], Optional["Tile"]]):
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass

    def __str__(self) -> str:
        return self.to_string()
