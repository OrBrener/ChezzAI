#!/usr/bin/env python3

from Chezz import *
# import sys

if __name__ == "__main__":

    game = Chezz()
    print(game)

    # if game.is_checkmate():
    #     print("It is the end of the game, you already won, good job! :)")
    # else:
    #     game.generate_board_files()
    game.generate_board_files()
            
