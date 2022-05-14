from datetime import datetime


class Logger:
    __BUFFER_SIZE = 1
    __instance = None

    @staticmethod
    def instance() -> "Logger":
        if Logger.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return Logger.__instance

    def __init__(self, seed: int):
        super().__init__("Qrogue-Logger")
        if Logger.__instance is not None:
            self.throw(Exception("This class is a singleton!"))
        else:
            self.__text = ""
            self.__message_popup = None
            self.__error_popup = None
            self.__buffer = []
            Logger.__instance = self

    @property
    def __buffer_size(self) -> int:
        return len(self.__buffer)

    @property
    def __is_in_debug_mode(self) -> bool:
        return True

    def __write(self, text) -> None:
        self.__buffer.append(text)
        if self.__buffer_size >= Logger.__BUFFER_SIZE:
            self.flush()

    def info(self, message, from_pycui: bool = True, **kwargs) -> None:
        time_str = datetime.now().strftime("%H-%M-%S")
        if from_pycui:
            self.__write(f"{{PyCUI}}{time_str}: {message}")
        else:
            self.__write(f"{{Qrogue}}{time_str}: {message}")

    def debug(self, msg: str, from_pycui: bool = True, *args, **kwargs) -> None:
        if self.__is_in_debug_mode:
            self.info(f"{{DEBUG}} |{msg}", from_pycui=from_pycui)

    def show_error(self, message) -> None:
        self.__error_popup("ERROR", str(message))

    def error(self, message, show: bool = True, from_pycui: bool = True, **kwargs) -> None:
        if show:
            self.__error_popup("ERROR", str(message))
        highlighting = "\n----------------------------------\n"
        self.info(f"{highlighting}ERROR |{message}{highlighting}", from_pycui=from_pycui)

    def throw(self, error) -> None:
        print(error)
        self.__write(f"[ERROR] {error}")
        self.flush()
        raise error

    def println(self, message: str = "", clear: bool = False) -> None:
        message = f"{message}\n"
        print(message)
        if clear:
            self.__text = message
        else:
            self.__text += message
        self.__message_popup("Logger", self.__text)

    def clear(self) -> None:
        self.__text = ""

    def flush(self) -> None:
        if self.__buffer_size > 0:
            text = ""
            for log in self.__buffer:
                text += log + "\n"
            print(text)
            self.__buffer = []