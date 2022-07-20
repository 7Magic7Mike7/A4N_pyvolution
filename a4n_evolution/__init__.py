import os

# from matplotlib import animation, pyplot as plt

from util.config import Config
from .interface import Interface
from .simulation.world.creatures.genome import Genome


def init(config_path: str):
    Config.load(config_path)
    Genome.activate_mutations(Config.instance().seed)


def test():
    Interface.init()
    for i in range(0, 100):
        print(Interface.get_data())


def create_animated_plot():
    def get_data_wrapper(*kwargs):
        Interface.get_data()

    Interface.init()
    """
    anim = animation.FuncAnimation(plt.gcf(), get_data_wrapper, frames=Config.instance().num_of_frames,
                                   interval=Config.instance().interval, repeat=False)
    plt.show()
    if Config.instance().save_animation:
        anim.save(os.path.join("data", "animated_plot.gif"))
    """
