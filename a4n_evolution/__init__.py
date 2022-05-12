from .interface import Interface


def test():
    Interface.init()
    for i in range (0, 10):
        print(Interface.get_data())
