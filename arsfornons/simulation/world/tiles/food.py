from typing import Callable, Optional, Tuple

import numpy as np

from arsfornons.simulation.world.tiles import Tile
from arsfornons.util.config import Config
from arsfornons.util.navigation import Coordinate


class Food(Tile):
    def __init__(self, pos: Coordinate, energy: float = 70):    # todo base engery to config
        super().__init__(pos)
        self.__energy = energy
        self.__age = 0

    def color(self) -> Tuple[float, float, float]:
        saturation = np.tanh(self.__energy)
        return 150, saturation, 0.8

    def eat_energy(self, eater: "Tile") -> float:
        return self.__energy

    def update(self,
               get_tile: Callable[[Optional[Coordinate], Optional[int], Optional[int]], Optional["Tile"]]) -> bool:
        self.__age += 1
        return self.__age < Config.instance().food_spoil_time

    def produced(self) -> Optional["Tile"]:
        return None

    def to_string(self) -> str:
        return "F"
