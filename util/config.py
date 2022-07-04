
class Config:
    @staticmethod
    def save_data() -> bool:
        return False

    @staticmethod
    def seed() -> int:
        return 1088

    @staticmethod
    def steps_per_populate_call() -> int:
        return 5

    @staticmethod
    def egg_incubation_time() -> int:
        return 7
