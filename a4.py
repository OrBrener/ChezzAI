#!/usr/bin/env python3

from Chezz import *
import argparse
import time

def main(func_name, *func_args):
    parser = argparse.ArgumentParser(description="Run different methods based on command-line flags.")
    
    parser.add_argument("--genBoardFile", type=int, action="store", help="generate a board input file given a board string")
    parsed_args = parser.parse_args()

    if parsed_args.genBoardFile:
        file_name = parsed_args.genBoardFile
        file_path = f"boards/{file_name}.txt"
        turn = sys.stdin.readline().strip()
        board_string = sys.stdin.read()
        Board.board_string_to_file(turn, board_string, file_path)
    else:
        def run_until_end_of_time_with_depth_n(depth):
            game = Chezz()
            total_time = game.time_allowed * 2
            iteration = 1
            all_scores = []
            while total_time > 0:
                print(game.board)
                start_time = time.time()
                if depth % 2 == 0:
                    best_move = game.max_score(game, depth)
                else:
                    best_move = game.min_score(game, depth)
                end_time = time.time()
                elapsed_time = (end_time - start_time)
                total_time = total_time - (elapsed_time * 1000)
                print(f"Iteration {iteration}: Time taken = {elapsed_time:.4f}, time left = {total_time * 1000} milliseconds")
                print(best_move)
                all_scores.append(best_move[0])
                iteration = iteration + 1

                game.board = game.board.generate_board_after_move(best_move[1])
            average_score = sum(all_scores) / len(all_scores) if all_scores else 0
            print(f"Average score: {average_score:.2f}")

        def run_n_times_with_given_depth(n, depth):
            game = Chezz()
            print(game)
            for _ in range(n):
                print(game.board)
                if game.is_checkmate():
                    print("Checkmate")
                best_move = game.max_score(game, depth)
                print("BEST MOVE", best_move)
                if isinstance(best_move, tuple):
                    game.board = game.board.generate_board_after_move(best_move[1])

        def get_best_move():
            game = Chezz()
            depth = 2
            if game.time_allowed - game.time_used < 10000:
                first_move = game.get_legal_moves(True)
                game.board.generate_board_files(first_move, 'stdout')
            else:
                best_move = game.max_score(game, depth)[1]
                game.board.generate_board_files([best_move], 'stdout')

        def test_heuristic():
            game = Chezz()
            print(game.board, game.heuristic(game.board))
            print(game.max_score(game, 2)[1])
        
        # Get the function by name and call it with additional arguments
        func = locals().get(func_name)
        if func:
            func(*func_args)
        else:
            print(f"Function '{func_name}' not found.")

if __name__ == "__main__":
    # main("run_until_end_of_time_with_depth_n", 3)
    # main("run_n_times_with_given_depth", 10, 3)
    # main("test_heuristic")
    
    main("get_best_move")

    # main("test_heuristic")

    # file_name = "test"
    # file_path = f"boards/{file_name}.txt"
    # turn = sys.stdin.readline().strip()
    # board_string = sys.stdin.read()
    # Board.board_string_to_file(turn, board_string, file_path)