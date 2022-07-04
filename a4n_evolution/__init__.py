import os

from matplotlib import animation, pyplot as plt

from util.config import Config
from .interface import Interface


def test():
    Interface.init()
    for i in range(0, 100):
        print(Interface.get_data())


def create_animated_plot():
    def get_data_wrapper(*kwargs):
        Interface.get_data()

    Interface.init()
    anim = animation.FuncAnimation(plt.gcf(), get_data_wrapper, frames=Config.num_of_frames(),
                                   interval=Config.interval(), repeat=False)
    plt.show()
    if Config.save_data():
        anim.save(os.path.join("data", "animated_plot.gif"))
