from typing import Callable, Optional, Tuple

import numpy as np

from a4n_evolution.simulation.world.tiles import Tile
from util.config import Config
from util.navigation import Coordinate


class Food(Tile):
    def __init__(self, pos: Coordinate, energy: float = 10):
        super().__init__(pos)
        self.__energy = energy
        self.__age = 0

    @property
    def energy(self) -> float:
        return self.__energy

    def color(self) -> Tuple[float, float, float]:
        saturation = np.tanh(self.__energy)
        return 150, saturation, 0.8

    def update(self,
               get_tile: Callable[[Optional[Coordinate], Optional[int], Optional[int]], Optional["Tile"]]) -> bool:
        self.__age += 1
        return self.__age < Config.instance().food_spoil_time

    def produced(self) -> Optional["Tile"]:
        return None

    def to_string(self) -> str:
        return "F"
