from Board import *
from itertools import chain
import copy
import os
import re

class Chezz:
    def __init__(self, board=None):
        if board:
            self.board = board
        else: 
            self.board = Board()
            self.board.populate_board()

    def __str__( self ):
        # return a string representation of the current state of the board and all the valid moves
        return_str = str(self.board)
        
        return_str += "Moves: \n"
        num_moves = 0
        for move in self.valid_moves():
            return_str += f"{num_moves+1}\t{move[0][1]}{move[2]}\n"
            num_moves += 1
        return_str += f"number of valid moves: {num_moves}"
        
        return return_str
    
    def valid_moves(self):
        def moves_flinger():
            moves = ["flinger"]
            
            return moves
            
        def moves_peon():
            moves = ["peon"]
            
            return moves

        def moves_knight():
            moves = ["knight"]
            
            return moves
        
        def moves_cannon():
            moves = ["cannon"]
            
            return moves
        
        def moves_queen():
            moves = ["queen"]
            
            return moves
        
        def moves_king():
            moves = []

            # for all kings on the board of the current turn's color (there can only be one):
            for position in self.board.get_piece_positions(self.board.colour+'K'):
                
                # get the coordinates of the piece position
                x, y = self.board.get_coordinates_at_position(position)  # Convert chess notation to (row, col)

                # Possible king moves (one square in any direction -- max of 8 moves)
                directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

                # for each possible move:
                for dx, dy in directions:
                    # coordinates after the move
                    new_x, new_y = x + dx, y + dy
                    # convert coordinates to board position (ex: (0,0) = 'a1') 
                    new_pos = self.board.convert_coordinates_to_position((new_x, new_y))
                    if new_pos != '' : # make sure that the move is within the boundary of the board
                        # retrieve the piece (or empty space) at the square of the move to be made
                        piece = self.board.get_piece_at_position(new_pos).strip()
                        if piece == '-' or piece[0] != self.board.colour: # check if the square is empty or has an opponent's piece 
                            # append valid move to the list
                            # format: (<piece to be moved>, <current piece position>, <new position after move>)
                            # ex: ('WK', 'd4', 'd5')
                            moves.append((self.board.colour+'K', position, new_pos))
            
            return moves
        
        def moves_zombie():
            moves = ["zombie"]
            
            return moves
        
        def moves_bishop():
            moves = ["bishop"]
            
            return moves
        
        def moves_rook():
            moves = ["rook"]
            
            return moves
        
        # move_functions = [moves_flinger, moves_peon, moves_knight, moves_cannon, 
        #               moves_queen, moves_king, moves_zombie, moves_bishop, moves_rook]

        move_functions = [moves_king]

        return list(chain.from_iterable(func() for func in move_functions))
    
    def generate_board_files(self):

        def remove_old_board_files():
            # Get a list of all files in the current directory
            files = os.listdir()
            
            # Define the pattern for board files with exactly three digits after "board."
            pattern = re.compile(r"^board\.\d{3}$")
            
            # Loop through the files and remove those that match the board pattern
            for file in files:
                if pattern.match(file):  # Check if the file matches the pattern "board.xxx"
                    os.remove(file)

        moves = self.valid_moves()
        remove_old_board_files()

        board_counter = 0
        for move in moves:
            new_board = self.generate_board_after_move(move)
            
            # Save the new board to a file
            filename = f"board.{str(board_counter).zfill(3)}"  # Name format: board.000, board.001, ...
            
            # open the output file and write the valid board encoding after the move
            with open(filename, 'w', encoding="utf-8") as file:
                file.write(f"{new_board.colour} {new_board.i1} {new_board.i2} {new_board.i3}\n")
                file.write("{\n")  # Open curly bracket

                # Sort board positions in correct order and write them to file
                piece_entries = []
                for (x, y), piece in sorted(new_board.board.items(), key=lambda item: (-item[0][1], item[0][0])):  
                    if piece.strip() != "-":
                        piece_entries.append(f"  {new_board.convert_coordinates_to_position((x,y))}: '{piece.strip()}'")

                # Join all entries with ",\n" and write them
                file.write(",\n".join(piece_entries) + "\n")

                file.write("}\n")  # Closing curly bracket

                # Write the final three lines
                file.write("0 0 0\n")


            board_counter += 1
    
    def generate_board_after_move(self, move):
        # modify the board state after applying the move.

        new_board = copy.deepcopy(self.board)  # Deep copy to avoid modifying the original board
        piece, pos, new_pos = move

        new_board.switch_turn()
        new_board.board[Board.position_map[pos]] = '-\t' # empty square where the piece used to be
        new_board.board[Board.position_map[new_pos]] = piece + '\t' # square where the piece is moving to is overwritten (either a simple movement of the piece or an opponent capture)

        # TODO: Implement contagion from zombie
        
        return new_board