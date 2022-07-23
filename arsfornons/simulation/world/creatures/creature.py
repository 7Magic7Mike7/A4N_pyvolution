from typing import Callable, Optional, Tuple

import numpy as np

from arsfornons.simulation.world.tiles import Tile
from arsfornons.simulation.world.creatures.genome import Genome, Brain
from arsfornons.util.config import Config
from arsfornons.util.navigation import Coordinate, Direction


class Creature(Tile):
    __World_Width = 1
    __World_Height = 1

    @staticmethod
    def set_world_dimension(width: int, height: int):
        if width <= 0:
            raise ValueError("Illegal world width!")
        if height <= 0:
            raise ValueError("Illegal world height!")
        Creature.__World_Width = width
        Creature.__World_Height = height

    @staticmethod
    def mateability(creature: "Creature", mate_tile: Tile) -> float:
        """
        Calculates how well the creatures can mate with each other.
        :param creature:
        :param mate_tile:
        :return: value in [0, 1.0]
        """
        if mate_tile is None:
            return 0
        if isinstance(mate_tile, Creature):
            # todo what about incest? how much are the genomes allowed to differ?
            return abs(creature.genome.value - mate_tile.genome.value)
        return 0

    @staticmethod
    def create(genome: str, pos: Coordinate, orientation: Direction, world_width: int,
               world_height: int) -> "Creature":
        return Creature(Genome(genome), pos, orientation, world_width, world_height)

    def __init__(self, genome: Genome, pos: Coordinate, orientation: Direction, world_width: int = __World_Width,
                 world_height: int = __World_Height):
        self.__world_width = world_width
        self.__world_height = world_height

        self.__genome = genome
        self.__brain = Brain(self.__genome)
        self.__age = 0
        self.__orientation = orientation
        self.__energy = self.__genome.max_energy
        self.__egg = None
        super(Creature, self).__init__(pos)

    @property
    def genome(self) -> Genome:
        return self.__genome

    @property
    def age(self) -> int:
        return self.__age

    def __validate_pos(self, pos: Coordinate) -> Coordinate:
        assert pos is not None

        return Coordinate(pos.x % self.__world_width, pos.y % self.__world_height)

    def color(self) -> Tuple[float, float, float]:
        hue = self.__genome.value * 360
        saturation = 0.2 + 0.8 * (self.__energy / self.__genome.max_energy)
        value = 0.4 + 0.6 - 0.6 * np.tanh(self.__age * 0.1)

        if hue < 0 or 360 <= hue:
            raise ValueError(f"Illegal value for hue: {hue}")
        if saturation < 0 or 1.0 < saturation:
            raise ValueError(f"Illegal value for saturation: {saturation}")
        if value < 0 or 1.0 < value:
            raise ValueError(f"Illegal value for value: {value}")

        return hue, saturation, value

    def eat_energy(self, eater: "Tile") -> float:
        return 0    # todo move to config

    def update(self, get_tile: Callable[[Optional[Coordinate], Optional[int], Optional[int]], Optional[Tile]]) -> bool:
        self.__age += 1

        lcd = 0
        dist = 3
        for i in range(1, dist + 1):
            pos = self.pos + self.__orientation * i
            if get_tile(pos, None, None):
                lcd += 1
            for j in range(1, i):
                turn_right = pos + self.__orientation.turn_right() * j
                turn_left = pos + self.__orientation.turn_left() * j
                if get_tile(turn_right, None, None):
                    lcd += 1
                if get_tile(turn_left, None, None):
                    lcd += 1
        lcd = lcd / dist**2     # with trigonometry we can see that the covered area is distance squared

        pos = self.__validate_pos(self.pos + self.__orientation)
        mate_tile = get_tile(pos, None, None)
        mate_ready = Creature.mateability(self, mate_tile)

        # inputs need to be between 0 and 1
        data = [
            np.tanh(self.__age),
            self.__energy / self.__genome.max_energy,
            self.pos.x / self.__world_width,
            self.pos.y / self.__world_height,
            Direction.to_float(self.__orientation),
            lcd,
            mate_ready,
        ]
        data = data[:Genome.NUM_OF_SENSORS]     # todo remove later to use all data
        output = self.__brain.think(np.array(data))
        driven_actuator = np.where(output == np.amax(output))[0][0]

        # self.__take_action(driven_actuator[0][0], mate_ready > 0.5)
        if driven_actuator in [0, 1]:
            self.__turn(driven_actuator)
        elif driven_actuator in [2, 3, 4, 5]:
            if mate_ready > 0:  # mate_ready implies that mate_tile is a Creature
                self.__mate(mate_tile)
            else:
                self.__move(driven_actuator)

        self.__energy -= 1 + abs(np.sum(output))
        return self.__energy > 0

    def __turn(self, value: int):
        if value == 0:
            self.__orientation.turn_left()
        else:
            self.__orientation.turn_right()

    def __move(self, value: int) -> bool:
        if value == 2:
            direction = self.__orientation
        elif value == 3:
            direction = self.__orientation.opposite()
        elif value == 4:
            direction = self.__orientation.turn_left()
        else:
            direction = self.__orientation.turn_right()
        new_pos = self._pos + direction
        self._pos = self.__validate_pos(new_pos)
        return True

    def __mate(self, mate_tile: "Creature"):
        egg_pos = self.__validate_pos(self.pos + self.__orientation.opposite())
        self.__egg = Egg(egg_pos, self.__orientation.opposite(), self, mate_tile)

    def produced(self) -> Optional["Tile"]:
        if self.__egg is None:
            return None
        else:
            egg = self.__egg
            self.__egg = None
            return egg

    def eat(self, food: Tile):
        self.__energy = min(self.__energy + food.eat_energy(self), self.genome.max_energy)

    def to_string(self) -> str:
        return "C"


class Egg(Tile):
    def __init__(self, pos: Coordinate, orientation: Direction, mother: Creature, father: Creature):
        super().__init__(pos)
        self.__orientation = orientation
        self.__genome = Genome.reproduce(mother.genome, father.genome)
        self.__age = 0
        self.__born_creature = None
        print("An egg was laid!")

    @property
    def orientation(self) -> Direction:
        return self.__orientation

    def color(self) -> Tuple[float, float, float]:
        value = 0.5 + 0.5 * (self.__age / Config.instance().egg_incubation_time)
        value = min(value, 1.0)
        return 250, 0.6, value

    def eat_energy(self, eater: "Tile") -> float:
        return 160   # todo move to config

    def update(self, get_tile: Callable[[Optional[Coordinate], Optional[int], Optional[int]], Optional["Tile"]]):
        self.__age += 1
        return self.__age <= Config.instance().egg_incubation_time

    def produced(self) -> Optional["Tile"]:
        if self.__age >= Config.instance().egg_incubation_time:
            self.__born_creature = Creature(self.__genome, self.pos, self.__orientation)
            # print("A creature was born!")
        return self.__born_creature

    def to_string(self) -> str:
        return "E"
