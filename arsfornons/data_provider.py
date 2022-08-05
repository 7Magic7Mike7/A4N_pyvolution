import json
import math
import os
import random
import requests
from abc import ABC, abstractmethod
from typing import Tuple, List, Optional

from util.util_functions import genome_to_hsv, hsv_to_rgb
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
            f'https://a4n-test.herokuapp.com/'
            f'retrieve?'
            f'simId={self.__sim_id}'
            '&'
            f'num={num}'
        )
        data = json.loads(response.text)
        data = data["data"]
        return data


class CacheDataProvider(DataProvider):
    class PrimeCalculator:
        __MAX_NUM = 10000000

        @staticmethod
        def __is_prime_factor(num: int, factor: int) -> bool:
            return num % factor == 0

        def __init__(self, seed: int):
            self.__rand = random.Random(seed)

        def calculate(self, manager: "CacheDataProvider.CacheManager"):
            num = self.__rand.randint(0, CacheDataProvider.PrimeCalculator.__MAX_NUM)
            start = int(math.sqrt(num))
            for i in range(start, 1, -1):
                if self.__is_prime_factor(num, i):
                    manager.add(num)

    class CacheItem:
        def __init__(self, value: int):
            self.__value = value
            self.__priority: int = 0

        @property
        def priority(self) -> int:
            return self.__priority

        def is_prime_factor_of(self, num: int) -> bool:
            if num % self.__value == 0:
                self.__priority += 1
                return True
            return False

        def to_gene_value(self) -> str:
            return f"{self.__value}{self.__priority}"

        def __lt__(self, other):
            if isinstance(other, CacheDataProvider.CacheItem):
                return self.priority < other.priority
            return True

        def __str__(self):
            return f"{self.__value}({self.__priority})"

    class CacheManager:
        __GENOME_LENGTH = 5 * 20

        def __init__(self, seed: int, cache_size: int = 7):
            self.__data: List[CacheDataProvider.CacheItem] = []
            self.__rand = random.Random(seed)
            self.__cache_size = cache_size

        def __store(self, value: int):
            item = CacheDataProvider.CacheItem(value)
            if len(self.__data) < self.__cache_size:
                self.__data.append(item)
            else:
                min_index = self.__data.index(min(self.__data))
                self.__data[min_index] = item

        def add(self, num: int) -> bool:
            for d in self.__data:
                if d.is_prime_factor_of(num):
                    return False
            self.__store(num)
            return True

        def produce_genome(self) -> str:
            genome = "".join([d.to_gene_value() for d in self.__data])
            self.__rand.shuffle(self.__data)
            return genome[:CacheDataProvider.CacheManager.__GENOME_LENGTH]

        def clear(self):
            self.__data.clear()

        def __str__(self):
            if len(self.__data) <= 0:
                return "[]"
            text = "["
            for d in self.__data:
                text += f"{d}, "
            return text[:-2] + "]"

    def __init__(self, seed: int, calculations_per_update: int = 5):
        super(CacheDataProvider, self).__init__()
        self.__calculator = CacheDataProvider.PrimeCalculator(seed)
        self.__manager = CacheDataProvider.CacheManager(seed)
        self.__genome = ""
        self.__calculations_per_update = calculations_per_update

    def request_new_data(self) -> None:
        for i in range(self.__calculations_per_update):
            self.__calculator.calculate(self.__manager)
        self.__genome = self.__manager.produce_genome()

    def get_raw_data(self) -> str:
        return self.__genome

    def get_prepared_data(self) -> Tuple[int, int, int]:
        if len(self.__genome) <= 0:
            return 0, 0, 0
        hsv = genome_to_hsv(self.__genome)
        return hsv_to_rgb(hsv)
