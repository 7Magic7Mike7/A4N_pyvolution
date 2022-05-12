
class RequestDecider:
    def __init__(self):
        self.__counter = 0

    def ever_x_steps(self, x: int):
        def should_request_new_data() -> bool:
            self.__counter += 1
            if x >= self.__counter:
                self.__counter = 0
                return True
            return False
        return should_request_new_data
