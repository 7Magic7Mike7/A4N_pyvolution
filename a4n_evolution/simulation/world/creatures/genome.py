from random import Random
from typing import List, Tuple

import numpy as np
import torch


class Genome:
    NUM_OF_SENSORS = 4
    NUM_OF_NEURONS = 3
    NUM_OF_ACTUATORS = 6
    GENE_LENGTH = 5
    NUM_OF_GENES = 20
    __WEIGHT_SIZE = 6
    __TARGET_SIZE = 5
    __SOURCE_SIZE = 5

    @staticmethod
    def reproduce(mother: "Genome", father: "Genome") -> "Genome":
        pass

    def __init__(self, data: str):
        self.__max_energy = 10   # two digits
        self.__aggression_level = 1     # 1 digit

        self.__i2o = np.zeros(shape=(Genome.NUM_OF_SENSORS, Genome.NUM_OF_ACTUATORS))
        self.__i2h = np.zeros(shape=(Genome.NUM_OF_SENSORS, Genome.NUM_OF_NEURONS))
        self.__h2h = np.zeros(shape=(Genome.NUM_OF_NEURONS, Genome.NUM_OF_NEURONS))
        self.__h2o = np.zeros(shape=(Genome.NUM_OF_NEURONS, Genome.NUM_OF_ACTUATORS))

        # 8 elements i20, 12 elements i2h, 9 elements h2h, 6 elements h20 -> 25 elements for NN

        # 5 digits make up a gene because 2^16 = 65 536
        # genome encoding:
        #       - 5 bit source id (input and neurons)
        #       - 5 bit target id (neurons and output)
        #       - 6 bit weight (-32...+32 normalized to -1.0...1.0)
        # if we have 16 genes for the brain, we would need 80 digits

        # 5 digits = 1 gene would for max_energy, aggression level, ???

        # sum = 85 digits
        index = 0
        cur_gene = int(data[index:index+Genome.GENE_LENGTH])
        self.__max_energy = 50 + cur_gene % 30
        index += Genome.GENE_LENGTH

        while index + Genome.GENE_LENGTH <= len(data):
            cur_gene = int(data[index:index+Genome.GENE_LENGTH])
            self.__create_brain_connection(cur_gene)
            index += Genome.GENE_LENGTH
        test = True

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


class _MyNN(torch.nn.Module):
    def __init__(self, n_in_features: int, n_out_features: int, layer_dimension: List[int]):
        super(_MyNN, self).__init__()
        nn = []
        hl_in = n_in_features
        for i in range(len(layer_dimension)):
            nn.append(torch.nn.Linear(hl_in, layer_dimension[i], bias=True))
            nn.append(torch.nn.ReLU())
            hl_in = layer_dimension[i]

        self.hidden_layers = torch.nn.Sequential(*nn)
        self.output_layer = torch.nn.Linear(hl_in, n_out_features, bias=True)

    def forward(self, x):
        """Apply CNN to input `x` of shape (N, n_channels, X, Y), where N=n_samples and X, Y are spatial dimensions"""
        nn_out = self.hidden_layers(x)  # apply hidden layers (N, n_in_channels, X, Y) -> (N, n_kernels, X, Y)
        pred = self.output_layer(nn_out)  # apply output layer (N, n_kernels, X, Y) -> (N, 1, X, Y)

        output_tensor = pred
        return output_tensor


class _OwnNN:
    def __init__(self, in_to_out: np.mat, in_to_hidden: np.mat, hidden_to_hidden: np.mat, hidden_to_out: np.mat):
        """
        First element is from in to out
        Second from in to hidden0
        Third from hidden0 to hidden0
        Fourth from hidden0 to hidden1
        ...
        Last from hidden X to out
        :param layer_matrices:
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
#static_test()
