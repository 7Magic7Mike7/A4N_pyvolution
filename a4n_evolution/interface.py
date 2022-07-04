
from a4n_evolution.data_provider import RandomDataProvider, FileDataProvider, ServerDataProvider
from a4n_evolution.evolution_data_provider import SimpleEvolSimDP


class Interface:
    __is_initialized = False
    __data_provider = None
    __counter = 0

    @staticmethod
    def init():
        #Interface.__data_provider = ServerDataProvider(sim_id=0)
        Interface.__data_provider = SimpleEvolSimDP()
        Interface.__is_initialized = True

    @staticmethod
    def get_data():
        if not Interface.__is_initialized:
            Interface.init()
        # print(f"get_data() #{Interface.__counter}")
        Interface.__counter += 1

        if Interface.__data_provider:
            data = Interface.__data_provider.get_prepared_data()
            Interface.__data_provider.request_new_data()
            return data
        else:
            raise RuntimeError("Data provider is uninitialized! Did you forget to call Interface.init()?")
