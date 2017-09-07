"""
Demeter example run.
"""

import os

from demeter.model import Demeter


def main():

    # path to config file
    ini = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')

    # instantiate Demeter
    dm = Demeter(config=ini)

    # run all time steps as set in config file
    dm.execute()


if __name__ == "__main__":

    main()