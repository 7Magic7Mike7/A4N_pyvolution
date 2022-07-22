from typing import Callable, Tuple

from arsfornons.data_provider import DataProvider, ServerDataProvider, RandomDataProvider, FileDataProvider
from arsfornons.simulation.request_decider import RequestDecider
from arsfornons.simulation.simulation import Simulation, SimpleSimulation
from arsfornons.simulation.world.creatures.genome import Genome
from arsfornons.util.config import Config


class EvolutionSimulationDataProvider(DataProvider):
    def __init__(self, simulation: Simulation, data_provider: DataProvider,
                 should_request_new_data: Callable[[], bool]):
        self.__simulation = simulation
        self.__base_data_provider = data_provider
        self.__should_request_new_data = should_request_new_data
        self.__new_data_available = False

    @property
    def _simulation(self) -> Simulation:
        return self.__simulation

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


class _EvolSimDP(EvolutionSimulationDataProvider):
    def __init__(self, data_provider: DataProvider):
        simulation = SimpleSimulation(Config.instance().seed)
        request_decider = RequestDecider()
        super(_EvolSimDP, self).__init__(simulation, data_provider,
                                         request_decider.ever_x_steps(Config.instance().steps_per_populate_call))

    def get_prepared_data(self) -> Tuple[int, int, int]:
        try:
            return super(_EvolSimDP, self).get_prepared_data()
        except:
            return self._simulation.to_channel_triple()


class SimpleEvolSimDP(_EvolSimDP):
    def __init__(self, sim_id: int):
        super(SimpleEvolSimDP, self).__init__(ServerDataProvider(sim_id))


class InfiniteFileEvolSimDP(_EvolSimDP):
    def __init__(self):
        super(InfiniteFileEvolSimDP, self).__init__(FileDataProvider())

