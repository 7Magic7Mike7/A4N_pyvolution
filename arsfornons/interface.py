from typing import List

from arsfornons.data_provider import DataProvider, RandomDataProvider, ServerDataProvider
from arsfornons.evolution_data_provider import SimpleEvolSimDP, InfiniteFileEvolSimDP, InfiniteRandomEvolSimDP
from arsfornons.util.config import Config


class Interface:
    __is_initialized = False
    __data_providers: List[DataProvider] = []

    @staticmethod
    def init():
        if Config.instance() is None:
            Config.load()  # create the default config
        # Interface.__data_provider = ServerDataProvider(sim_id=0)
        Interface.__data_providers = [
            ServerDataProvider(0),
            ServerDataProvider(1),
            ServerDataProvider(2),
            ServerDataProvider(3),
            ServerDataProvider(4),
            ServerDataProvider(5),
            ServerDataProvider(6),
            ServerDataProvider(7),
            InfiniteFileEvolSimDP(),
            InfiniteRandomEvolSimDP(Config.instance().seed),
        ]
        Interface.__is_initialized = True

    @staticmethod
    def get_data(index: int):
        if not Interface.__is_initialized:
            Interface.init()

        if 0 <= index < len(Interface.__data_providers):
            Config.activate_index(index)
            data_provider = Interface.__data_providers[index]
            data = data_provider.get_prepared_data()
            data_provider.request_new_data()
            return data
        else:
            raise RuntimeError(f"Invalid index provided: {index}. Must be between 0 and "
                               f"{len(Interface.__data_providers)}")
