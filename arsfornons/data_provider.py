import json
import os
import random
import requests
from abc import ABC, abstractmethod
from typing import Tuple, List, Optional

from arsfornons.simulation.world.creatures.genome import Genome


class DataProvider(ABC):
    @abstractmethod
    def request_new_data(self) -> None:
        """
        Readies data for next get_raw_data() or get_prepared_data() call.
        :return: None
        """
        pass

    @abstractmethod
    def get_raw_data(self) -> str:
        pass

    @abstractmethod
    def get_prepared_data(self) -> Tuple[int, int, int]:
        """

        :return: three ints in the range [0, 255]
        """
        pass


class RandomDataProvider(DataProvider):
    def __init__(self, seed: int = 7):
        super(RandomDataProvider, self).__init__()
        self.__rand = random.Random(seed)

    def request_new_data(self) -> None:
        pass

    def get_raw_data(self) -> str:
        # data = self.get_prepared_data()
        # return f"{data[0]}{data[1]}{data[2]}"
        data = ""
        for i in range(Genome.NUM_OF_GENES):
            value = self.__rand.randint(0, 10**Genome.GENE_LENGTH)
            data += format(value, f"0{Genome.GENE_LENGTH}d")
        return data

    def get_prepared_data(self) -> Tuple[int, int, int]:
        r = self.__rand.randint(0, 255)
        g = self.__rand.randint(0, 255)
        b = self.__rand.randint(0, 255)
        return r, g, b


class FileDataProvider(DataProvider):
    # D:\Documents\pycharm_workspace\TestProject\data\a4n\s0.txt
    __PATH = os.path.join(os.path.dirname(__file__), "data", "cache_data.txt")

    @staticmethod
    def read(path: str) -> str:
        if os.path.exists(path):
            with open(path, "r") as file:
                content = file.read()
            return content

    def __init__(self, path: str = __PATH):
        data = self.read(path).splitlines()
        self.__data = [d.replace(" ", "") for d in data]    # remove spaces between genes
        self.__index = 0

    def request_new_data(self) -> None:
        self.__index += 1
        if self.__index >= len(self.__data):
            self.__index = 0

    def get_raw_data(self) -> str:
        return self.__data[self.__index]

    def get_prepared_data(self) -> Tuple[int, int, int]:
        cur_dat = self.__data[self.__index]
        parts = cur_dat.split(" ")
        parts = [int(d) % 255 for d in parts]
        return parts[0], parts[1], parts[2]


class ServerDataProvider(DataProvider):
    __BUFFER_HALF_SIZE = 5
    __NO_DATA = (0, 0, 0)

    def __init__(self, sim_id: int):
        self.__buffer: List[Optional[str]] = [None] * (self.__BUFFER_HALF_SIZE * 2)
        self.__index = 0
        self.__sim_id = sim_id
        self.__fill_buffer(start=0, num=self.__buffer_size)

    @property
    def __buffer_size(self) -> int:
        return self.__BUFFER_HALF_SIZE * 2

    def request_new_data(self) -> None:
        self.__index += 1
        if self.__index >= self.__buffer_size:
            self.__index = 0

        if self.__buffer[self.__index] is None:
            self.__fill_buffer(start=self.__index, num=min(self.__BUFFER_HALF_SIZE, self.__buffer_size - self.__index))

    def get_raw_data(self) -> str:
        data = self.__buffer[self.__index]
        if data:
            self.__buffer[self.__index] = None
            return data
        else:
            return ""

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
            if start + i >= self.__buffer_size or i >= len(new_data) or new_data[i] is None:
                break
            # print(f"filled buffer at {start + i}")
            self.__buffer[start + i] = new_data[i]

    def __http_get(self, num: int = __BUFFER_HALF_SIZE) -> List[str]:
        response = requests.get(
            f'https://www.arsfornons.com/'
            f'retrieve?'
            f'simId={self.__sim_id}'
            '&'
            f'num={num}'
        )
        data = json.loads(response.text)
        data = data["data"]
        return data
