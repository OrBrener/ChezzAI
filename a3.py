#!/usr/bin/env python3

from Chezz import *
# import sys

if __name__ == "__main__":

    board = Board()
    board.populate_board()

    game = Chezz(board)
    print(game)
