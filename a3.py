#!/usr/bin/env python3

from Chezz import *
# import sys

if __name__ == "__main__":

    game = Chezz()
    print(game)
    print(game.valid_moves())
    game.generate_board_files()
