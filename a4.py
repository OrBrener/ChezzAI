#!/usr/bin/env python3

from Chezz import *
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run different methods based on command-line flags.")
    
    parser.add_argument("--genBoardFile", type=int, action="store", help="generate a board input file given a board string")
    args = parser.parse_args()

    if args.genBoardFile:
        file_name = args.genBoardFile
        file_path = f"boards/{file_name}.txt"
        turn = sys.stdin.readline().strip()
        board_string = sys.stdin.read()
        Board.board_string_to_file(turn, board_string, file_path)
    else:
        game = Chezz()
        game.board.generate_board_files([game.valid_moves()[0]])
        # print(game)

        # if game.is_checkmate():
        #     print("It is the end of the game, you already won, good job! :)")
        # else:
        #     game.board.generate_board_files(game.valid_moves())      


if __name__ == "__main__":
    main()          
