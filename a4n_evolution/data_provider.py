import json
import os
import random
import requests
from abc import ABC, abstractmethod
from typing import Tuple, List, Callable

from a4n_evolution.simulation.simulation import Simulation, SimpleSimulation


class DataProvider(ABC):
    @abstractmethod
    def request_new_data(self) -> None:
        """
        Readies data for next get_prepared_data() call.
        :return: None
        """
        pass

    @abstractmethod
    def get_prepared_data(self) -> Tuple[int, int, int]:
        """

        :return: three ints in the range [0, 255]
        """
        pass


class RandomDataProvider(DataProvider):
    def request_new_data(self) -> None:
        pass

    def get_prepared_data(self) -> Tuple[int, int, int]:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return r, g, b


class FileDataProvider(DataProvider):
    # D:\Documents\pycharm_workspace\TestProject\data\a4n\s0.txt
    __PATH = os.path.join("D:\\", "Documents", "pycharm_workspace", "TestProject", "data", "a4n", "s0.txt")

    @staticmethod
    def read(path: str) -> str:
        if os.path.exists(path):
            with open(path, "r") as file:
                content = file.read()
            return content

    def __init__(self, path: str = __PATH):
        self.__data = self.read(path).splitlines()
        self.__index = 0

    def request_new_data(self) -> None:
        self.__index += 1
        if self.__index >= len(self.__data):
            self.__index = 0

    def get_prepared_data(self) -> Tuple[int, int, int]:
        cur_dat = self.__data[self.__index]
        parts = cur_dat.split(" ")
        parts = [int(d) % 255 for d in parts]
        return parts[0], parts[1], parts[2]


class ServerDataProvider(DataProvider):
    __BUFFER_HALF_SIZE = 5
    __NO_DATA = (0, 0, 0)

    def __init__(self, sim_id: int):
        self.__buffer = [None] * (self.__BUFFER_HALF_SIZE * 2)
        self.__index = 0
        self.__sim_id = sim_id
        self.__fill_buffer(start=0, num=len(self.__buffer))

    def request_new_data(self) -> None:
        self.__index += 1
        if self.__index >= len(self.__buffer):
            self.__index = 0

        if self.__buffer[self.__index] is None:
            self.__fill_buffer(start=self.__index, num=min(self.__BUFFER_HALF_SIZE, len(self.__buffer) - self.__index))

    def get_prepared_data(self) -> Tuple[int, int, int]:
        # todo prepare data to the needed output
        data = self.__buffer[self.__index]
        if data:
            self.__buffer[self.__index] = None
            a = int(data[0:3]) % 255
            b = int(data[3:6]) % 255
            c = int(data[6:9]) % 255
            return a, b, c
        else:
            return self.__NO_DATA

    def __fill_buffer(self, start: int, num: int = __BUFFER_HALF_SIZE):
        new_data = self.__http_get(num)
        for i in range(num):
            if start + i >= len(self.__buffer) or i >= len(new_data) or new_data[i] is None:
                break
            print(f"filled buffer at {start + i}")
            self.__buffer[start + i] = new_data[i]

    def __http_get(self, num: int = __BUFFER_HALF_SIZE) -> List[str]:
        response = requests.get(
            f'https://arsfornons.glitch.me/retrieve?'
            f'simId={self.__sim_id}'
            '&'
            f'num={num}'
        )
        data = json.loads(response.text)["data"]
        return data
