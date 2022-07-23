import os
from typing import Optional, List


class Config:
    __instances: List["Config"] = []
    __active_index: int = 0

    @staticmethod
    def load(path: str, reset: bool = False):
        if reset:
            Config.__instances = []

        if os.path.exists(path):
            with open(path, "r") as file:
                content = file.readlines()

                def cbool(index: int) -> bool:
                    return content[index].lower() in ["yes", "true"]

                def cint(index: int) -> int:
                    return int(content[index])

                def cfloat(index: int) -> float:
                    return float(content[index])

                Config(cbool(0), cint(1), cint(2), cbool(3),
                       cint(4),
                       cint(5), cint(6), cfloat(7), cint(8),
                       cint(9),
                       cint(10), cint(11), cint(12), cint(13), cbool(14))
        else:
            raise FileNotFoundError(f"Config file does not exist: {os.path.abspath(path)}")

        cfs = [Config()] * 10    # custom configs for testing
        cfs[1].__food_spoil_time = 1000000   # food "never" spoils
        cfs[2].__populate_calls_per_food_spawn = 0    # food never spawns
        cfs[3].__egg_incubation_time = 1    # eggs instantly hatch
        cfs[4].__mutation_chance = 0.5      # high mutation chance
        cfs[5].__world_size = 6             # extra small world
        cfs[6].__world_size = 1500          # extra big world
        cfs[7].__allow_egg_eating = True    # allow eating of eggs
        # cfs[8] do nothing special since the data provider is already custom
        # fast creature spawns for random data
        cfs[9].__populate_calls_per_creature_spawn = 1
        cfs[9].__steps_per_populate_call = 1

        Config.__instances += cfs[1:]   # ignore the first one since it's only here for readability

    @staticmethod
    def instance() -> Optional["Config"]:
        return Config.__instances[Config.__active_index]

    @staticmethod
    def activate_index(index: int):
        assert 0 <= index < len(Config.__instances)
        Config.__active_index = index

    @staticmethod
    def add_config(config: "Config"):
        Config.__instances.append(config)

    def __init__(self,
                 save_animation: bool = False, interval: int = 16, num_of_frames: int = 3600, save_plots: bool = False,
                 steps_per_plot: int = 50,
                 seed: int = 1088, world_size: int = 300, mutation_chance: float = 0.001, min_max_energy: int = 500,
                 max_bonus_energy: int = 300,
                 steps_per_populate_call: int = 3, populate_calls_per_creature_spawn: int = 2,
                 populate_calls_per_food_spawn: int = 1, egg_incubation_time: int = 7, food_spoil_time: int = 50,
                 allow_egg_eating: bool = False):
            self.__save_animation = save_animation
            self.__interval = interval      # in ms
            self.__num_of_frames = num_of_frames
            self.__save_plots = save_plots
            self.__steps_per_plot = steps_per_plot

            self.__seed = seed
            self.__world_size = world_size
            self.__mutation_chance = mutation_chance
            self.__min_max_energy = min_max_energy
            self.__max_bonus_energy = max_bonus_energy

            self.__steps_per_populate_call = steps_per_populate_call
            self.__populate_calls_per_creature_spawn = populate_calls_per_creature_spawn
            self.__populate_calls_per_food_spawn = populate_calls_per_food_spawn
            self.__egg_incubation_time = egg_incubation_time
            self.__food_spoil_time = food_spoil_time
            self.__allow_egg_eating = allow_egg_eating

            if len(Config.__instances) == 0:
                Config.__instances.append(self)

# ANIMATION
    @property
    def save_animation(self) -> bool:
        return self.__save_animation

    @property
    def interval(self) -> int:
        return self.__interval

    @property
    def num_of_frames(self) -> int:
        return self.__num_of_frames

# PLOTS
    @property
    def save_plots(self) -> bool:
        return self.__save_plots

    @property
    def steps_per_plot(self) -> int:
        return self.__steps_per_plot

# SIMULATION
    @property
    def seed(self) -> int:
        return self.__seed

    @property
    def world_size(self) -> int:
        return self.__world_size

    @property
    def mutation_chance(self) -> float:
        return self.__mutation_chance

    @property
    def min_max_energy(self) -> int:
        return self.__min_max_energy

    @property
    def max_bonus_energy(self) -> int:
        return self.__max_bonus_energy

# TILES

    @property
    def steps_per_populate_call(self) -> int:
        return self.__steps_per_populate_call

    @property
    def populate_calls_per_creature_spawn(self) -> int:
        return self.__populate_calls_per_creature_spawn

    @property
    def populate_calls_per_food_spawn(self) -> int:
        return self.__populate_calls_per_food_spawn

    @property
    def egg_incubation_time(self) -> int:
        return self.__egg_incubation_time

    @property
    def food_spoil_time(self) -> int:
        return self.__food_spoil_time

    @property
    def allow_egg_eating(self) -> bool:
        return self.__allow_egg_eating
