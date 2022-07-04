from matplotlib import animation, pyplot as plt
from .interface import Interface


def test():
    nums_a = [12346, 47291, 98347, 48295, 80425, 17894]
    nums_b = [48295, 80425, 17894, 12346, 47291, 98347]
    nums_c = [99999, 11122, 34125, 90909, 10000, 47184]
    nums_d = [12300, 41000, 72569, 39835, 70000, 14892]
    factors = [2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37]
    values = []
    for nums in [nums_a, nums_b, nums_c, nums_d]:
        value = 0
        for i, num in enumerate(nums):
            value += num * factors[i]
        values.append(value / (10**5 * sum(factors[0:len(nums)])))

    debug = True


    Interface.init()
    for i in range(0, 100):
        print(Interface.get_data())


def create_animated_plot():
    def get_data_wrapper(*kwargs):
        Interface.get_data()

    Interface.init()
    anim = animation.FuncAnimation(plt.gcf(), get_data_wrapper, interval=16)
    plt.show()
