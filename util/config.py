
class Config:

# ANIMATION
    @staticmethod
    def save_animation() -> bool:
        return True

    @staticmethod
    def interval() -> int:
        return 16

    @staticmethod
    def num_of_frames() -> int:
        return 60 * 60

# PLOTS
    @staticmethod
    def save_plots() -> bool:
        return True

    @staticmethod
    def steps_per_plot() -> int:
        return 50

# SIMULATION
    @staticmethod
    def seed() -> int:
        return 1088

    @staticmethod
    def world_size() -> int:
        return 300      # should be dividable by 3 for rgb conversion

    @staticmethod
    def mutation_chance() -> float:
        return 0.001

    @staticmethod
    def min_max_energy() -> int:
        return 500

# TILES
    @staticmethod
    def max_bonus_energy() -> int:
        return 300

    @staticmethod
    def steps_per_populate_call() -> int:
        return 3

    @staticmethod
    def egg_incubation_time() -> int:
        return 7

    @staticmethod
    def food_spoil_time() -> int:
        return 50
