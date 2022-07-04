from matplotlib import animation, pyplot as plt
from .interface import Interface


def test():
    Interface.init()
    for i in range(0, 100):
        print(Interface.get_data())


def create_animated_plot():
    def get_data_wrapper(*kwargs):
        Interface.get_data()

    Interface.init()
    anim = animation.FuncAnimation(plt.gcf(), get_data_wrapper, interval=16)
    plt.show()
