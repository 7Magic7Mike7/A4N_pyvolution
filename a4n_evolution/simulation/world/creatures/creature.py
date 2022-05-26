from typing import Callable, Optional, Tuple

import numpy as np

from a4n_evolution.simulation.world import World
from a4n_evolution.simulation.world.creatures.genome import Genome, Brain
from util.navigation import Coordinate, Direction
from a4n_evolution.simulation.world.tiles import Tile


class Creature(Tile):
    def __init__(self, genome: str, pos: Coordinate, orientation: Direction, world_width: int, world_height: int):
        self.__world_width = world_width
        self.__world_height = world_height

        self.__genome = Genome(genome)
        self.__brain = Brain(self.__genome)
        self.__age = 0
        self.__orientation = orientation
        self.__energy = self.__genome.max_energy
        super(Creature, self).__init__(pos)

    @property
    def genome(self) -> Genome:
        return self.__genome

    @property
    def age(self) -> int:
        return self.__age

    def color(self) -> Tuple[float, float, float]:
        hue = self.__genome.value
        saturation = 0.2 + 0.8 * (self.__energy / self.__genome.max_energy)
        value = 0.5 + 0.5 * np.tanh(self.__age)
        return hue, saturation, value

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

        # inputs need to be between 0 and 1
        data = [
            np.tanh(self.__age), self.__energy / self.__genome.max_energy,
            self.pos.x / self.__world_width, self.pos.y / self.__world_height, self.__orientation,
            lcd,
        ]
        data = data[:Genome.NUM_OF_SENSORS]     # todo remove later to use all data
        output = self.__brain.think(np.array(data))
        driven_actuator = np.where(output == np.amax(output))
        self.__take_action(driven_actuator[0][0])
        self.__energy -= np.sum(output)

        return self.__energy > 0

    def __take_action(self, actuator: int):
        if actuator == 0:       # turn left
            self.__orientation.turn_left()
        elif actuator == 1:     # turn right
            self.__orientation.turn_right()
        elif actuator == 2:     # move forward
            self.__move(self.__orientation)
        elif actuator == 3:     # move backward
            self.__move(self.__orientation.opposite())
        elif actuator == 4:     # move left
            self.__move(self.__orientation.turn_left())
        elif actuator == 5:     # move right
            self.__move(self.__orientation.turn_right())

    def __move(self, direction: Direction) -> bool:
        new_pos = self._pos + direction
        if 0 <= new_pos.x < self.__world_width and 0 <= new_pos.y < self.__world_height:
            self._pos = new_pos
            return True
        return False

    def to_string(self) -> str:
        return "C"


class Egg(Tile):
    def __init__(self, pos: Coordinate, orientation: Direction, mother: Creature, father: Creature):
        super().__init__(pos)
        self.__orientation = orientation
        self.__genome = Genome.reproduce(mother.genome, father.genome)

    @property
    def orientation(self) -> Direction:
        return self.__orientation

    def update(self, get_tile: Callable[[Optional[Coordinate], Optional[int], Optional[int]], Optional["Tile"]]):
        pass    # todo how to set new tile at position?

    def to_string(self) -> str:
        return "E"
