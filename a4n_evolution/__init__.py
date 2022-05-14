from .interface import Interface


def test():
    Interface.init()
    for i in range(0, 100):
        print(Interface.get_data())
