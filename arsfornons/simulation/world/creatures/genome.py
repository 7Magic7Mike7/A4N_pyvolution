from random import Random
from typing import Optional

import numpy as np

from arsfornons.util.config import Config


class Genome:
    NUM_OF_SENSORS = 7
    NUM_OF_NEURONS = 3
    NUM_OF_ACTUATORS = 6
    GENE_LENGTH = 5
    NUM_OF_GENES = 20
    # MAX_VALUE = 10**(GENE_LENGTH * NUM_OF_GENES)
    __WEIGHT_SIZE = 6
    __TARGET_SIZE = 5
    __SOURCE_SIZE = 5

    __rand: Optional[Random] = None

    @staticmethod
    def activate_mutations(seed: int):
        Genome.__rand = Random(seed)

    @staticmethod
    def reproduce(mother: "Genome", father: "Genome") -> "Genome":
        genome = ""
        for i in range(Genome.NUM_OF_GENES):
            if Genome.__rand is not None and Genome.__rand.random() < Config.instance().mutation_chance:
                child: int = Genome.__rand.randint(0, 10**Genome.GENE_LENGTH)
            else:
                gene_start = i * Genome.GENE_LENGTH
                gene_end = (i+1) * Genome.GENE_LENGTH
                m = int(mother.__data[gene_start:gene_end])
                f = int(father.__data[gene_start:gene_end])

                if Genome.__rand is None:
                    mom_ratio = 0.5
                else:
                    mom_ratio = Genome.__rand.random()
                child: int = round(m * mom_ratio + f * (1.0 - mom_ratio))
            genome += format(child, f"0{Genome.GENE_LENGTH}d")
        return Genome(genome)

    def __init__(self, data: str):
        self.__data = data
        self.__max_energy = 10   # two digits
        self.__aggression_level = 1     # 1 digit

        self.__i2o = np.zeros(shape=(Genome.NUM_OF_SENSORS, Genome.NUM_OF_ACTUATORS))
        self.__i2h = np.zeros(shape=(Genome.NUM_OF_SENSORS, Genome.NUM_OF_NEURONS))
        self.__h2h = np.zeros(shape=(Genome.NUM_OF_NEURONS, Genome.NUM_OF_NEURONS))
        self.__h2o = np.zeros(shape=(Genome.NUM_OF_NEURONS, Genome.NUM_OF_ACTUATORS))

        self.__value = 0

        # 8 elements i2o, 12 elements i2h, 9 elements h2h, 6 elements h2o -> 25 elements for NN

        # 5 digits make up a gene because 2^16 = 65 536
        # genome encoding:
        #       - 5 bit source id (input and neurons)
        #       - 5 bit target id (neurons and output)
        #       - 6 bit weight (-32...+32 normalized to -1.0...1.0)
        # if we have 16 genes for the brain, we would need 80 digits

        # 5 digits = 1 gene for max_energy, aggression level, ???

        # sum = 85 digits
        index = 0
        cur_gene = int(data[index:index+Genome.GENE_LENGTH])
        self.__max_energy = Config.instance().min_max_energy + cur_gene % Config.instance().max_bonus_energy
        index += Genome.GENE_LENGTH

        while index + Genome.GENE_LENGTH <= len(data):
            cur_gene = int(data[index:index+Genome.GENE_LENGTH])
            self.__create_brain_connection(cur_gene)
            index += Genome.GENE_LENGTH

            self.__value += (cur_gene / 10**Genome.GENE_LENGTH)

        self.__value = np.tanh(self.__value)

    def __create_brain_connection(self, cur_gene: int):
        weight = cur_gene % (2 ** Genome.__WEIGHT_SIZE)
        cur_gene = int(cur_gene / 2 ** Genome.__WEIGHT_SIZE)
        target = cur_gene % (2 ** Genome.__TARGET_SIZE)
        cur_gene = int(cur_gene / 2 ** Genome.__TARGET_SIZE)
        source = cur_gene % (2 ** Genome.__SOURCE_SIZE)

        # normalize the data
        source = source % (Genome.NUM_OF_SENSORS + Genome.NUM_OF_NEURONS)
        target = target % (Genome.NUM_OF_NEURONS + Genome.NUM_OF_ACTUATORS)
        weight = (weight - 2 ** (Genome.__WEIGHT_SIZE - 1)) / 2 ** (Genome.__WEIGHT_SIZE - 1)

        if source < Genome.NUM_OF_SENSORS:
            if target < Genome.NUM_OF_NEURONS:
                self.__i2h[source][target] = weight
            else:
                target -= Genome.NUM_OF_NEURONS
                self.__i2o[source][target] = weight
        else:
            source -= Genome.NUM_OF_SENSORS
            if target < Genome.NUM_OF_NEURONS:
                self.__h2h[source][target] = weight
            else:
                target -= Genome.NUM_OF_NEURONS
                self.__h2o[source][target] = weight

    @property
    def max_energy(self) -> float:
        return self.__max_energy

    @property
    def in_to_out(self) -> np.mat:
        return self.__i2o

    @property
    def in_to_hidden(self) -> np.mat:
        return self.__i2h

    @property
    def hidden_to_hidden(self) -> np.mat:
        return self.__h2h

    @property
    def hidden_to_out(self) -> np.mat:
        return self.__h2o

    @property
    def value(self) -> float:
        """

        :return: float in [0, 1.0]
        """
        return self.__value


class Brain:
    # sensors (input)
    # Age, Energy Level
    # Position, Orientation
    # Look Cone Density (how much stuff is inside the look cone),
    # Food Distance, Food Direction (Vector angle),
    # Mate Distance, Mate Direction
    # Pheromone Distance, Pheromone Direction

    # actuators (output)
    # Turn Left, Turn Right, Move Forward, Move Backward, Move Left, Move Right
    # (Energy spent = sum of outputs?)

    def __init__(self, genome: Genome):
        # self.__nn = _MyNN(Genome.NUM_OF_SENSORS, Genome.NUM_OF_ACTUATORS, [])
        self.__nn = _OwnNN(
            genome.in_to_out,
            genome.in_to_hidden,
            genome.hidden_to_hidden,
            genome.hidden_to_out
        )

    def think(self, data: np.ndarray) -> np.ndarray:
        """

        :param data: sensory input
        :return: actuator output
        """
        return self.__nn.forward(data)


class _OwnNN:
    def __init__(self, in_to_out: np.mat, in_to_hidden: np.mat, hidden_to_hidden: np.mat, hidden_to_out: np.mat):
        """
        First element is from in to out
        Second from in to hidden0
        Third from hidden0 to hidden0
        Fourth from hidden0 to hidden1
        ...
        Last from hidden X to ou
        """
        self.__i2o = in_to_out
        self.__i2h = in_to_hidden
        self.__h2h = hidden_to_hidden
        self.__h2o = hidden_to_out

        self.__prev_hidden_data = np.ones((1, self.__h2h.shape[0]))

    def forward(self, sensor_input: np.ndarray) -> np.ndarray:
        sensor_input = np.mat(sensor_input)
        out_data = sensor_input.dot(self.__i2o)

        hidden_data = sensor_input.dot(self.__i2h) + self.__prev_hidden_data.dot(self.__h2h)
        self.__prev_hidden_data = hidden_data

        out_data += (hidden_data.dot(self.__h2o))
        return out_data.A1


def static_test():
    rand = Random(7)
    for i in range(100000):
        print(f"run {i}")
        data = ""
        for j in range(Genome.NUM_OF_GENES):
            data += str(rand.randint(10**(Genome.GENE_LENGTH-1), 10**Genome.GENE_LENGTH))
        genome = Genome(data)

        brain = Brain(genome)
        sensor_input = []
        for j in range(Genome.NUM_OF_SENSORS):
            sensor_input.append(rand.random())
        test = brain.think(np.array(sensor_input))
        print(test)
# static_test()