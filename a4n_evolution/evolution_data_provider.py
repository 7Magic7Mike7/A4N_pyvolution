from typing import Callable, Tuple

from a4n_evolution.data_provider import DataProvider, RandomDataProvider, ServerDataProvider
from a4n_evolution.simulation.request_decider import RequestDecider
from a4n_evolution.simulation.simulation import Simulation, SimpleSimulation
from a4n_evolution.simulation.world.creatures.genome import Genome
from util.config import Config


class EvolutionSimulationDataProvider(DataProvider):
    def __init__(self, simulation: Simulation, data_provider: DataProvider,
                 should_request_new_data: Callable[[], bool]):
        self.__simulation = simulation
        self.__base_data_provider = data_provider
        self.__should_request_new_data = should_request_new_data
        self.__new_data_available = False

    def request_new_data(self) -> None:
        if self.__should_request_new_data():
            self.__base_data_provider.request_new_data()
            self.__new_data_available = True
        self.__simulation.process_step()

    def get_raw_data(self) -> str:
        return "TODO"

    def get_prepared_data(self) -> Tuple[int, int, int]:
        if self.__new_data_available:
            data = self.__base_data_provider.get_raw_data()
            if len(data) == 0:
                raise Exception("Data not available!!!")
            data_length = Genome.GENE_LENGTH * Genome.NUM_OF_GENES
            while len(data) < data_length:
                data += data
            data = data[:data_length]
            self.__simulation.populate(data)
            self.__new_data_available = False
        return self.__simulation.to_channel_triple()


class SimpleEvolSimDP(EvolutionSimulationDataProvider):
    def __init__(self):
        simulation = SimpleSimulation(Config.instance().seed)
        data_provider = RandomDataProvider(Config.instance().seed)
        # data_provider = ServerDataProvider(sim_id=0)
        request_decider = RequestDecider()
        super(SimpleEvolSimDP, self).__init__(simulation, data_provider,
                                              request_decider.ever_x_steps(Config.instance().steps_per_populate_call))
