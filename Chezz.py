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
        return str(self.board)
    
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
                    print(f"Removed file: {file}")

        # Generate all possible boards for each move

        moves = self.valid_moves()
        remove_old_board_files()

        board_counter = 0
        for move in moves:
            print(move)
            new_board = self.generate_board_after_move(move)  # Function to update the board state
            
            # Save the new board to a file
            filename = f"board.{str(board_counter).zfill(3)}"  # Name format: board.000, board.001, etc.
            
            with open(filename, 'w') as file:
                file.write(new_board)  # Assuming generate_board_after_move returns a board string

            board_counter += 1
    
    def generate_board_after_move(self, move):
        # Logic to modify the board state after applying the move.
        # This is a placeholder, and you will need to implement how the board changes based on the move.
        # Return the updated board as a string.
        new_board = copy.deepcopy(self.board)  # Deep copy to avoid modifying the original board
        # Apply the move to the new_board here...
        return str(str(new_board) + move)  # Convert the new board to string format for output