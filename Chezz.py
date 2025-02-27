from Board import *
from Piece import *
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

        # Directionality for Peons
        forward = 1 if self.board.colour == 'w' else -1  # White moves up, Black moves down

        # Define pieces with their name, move_directions, capture_directions, single_step_movement, single_step_capture, special_abilities
        # TODO: Reorder the pieces from most important to least so that the order of the moves is more efficient for A4
        pieces = [
            Piece('K', [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)], single_step_capture=True, single_step_movement=True),
            Piece('B', [(-1, -1), (-1, 1), (1, -1), (1, 1)]),
            Piece('R', [(-1, 0), (1, 0), (0, -1), (0, 1)]),
            Piece('Q', [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]),
            Piece('N', [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)], single_step_capture=True, single_step_movement=True),
            Piece('P', [(0, forward)], capture_directions=[(-1, forward), (1, forward)], single_step_capture=True, single_step_movement=True)
        ]

        def generate_moves(piece):
            '''
            Returns a list of moves (piece movement to an empty square, or a piece capture) 
            for all of the instances of the given piece on the current board
            '''
            # TODO: Reorder the move appends to captures before simple movement so that the order of the moves is more efficient for A4
            moves = []

            # Get all positions of the given piece type
            for position in self.board.get_piece_positions(self.board.colour + piece.name):
                x, y = self.board.get_coordinates_at_position(position) # Convert chess notation to (row, col)
                
                # Loop through each movement and capture direction
                for dx, dy in set(piece.move_directions + piece.capture_directions):  
                    new_x, new_y = x + dx, y + dy
                    # Convert coordinates to board position (ex: (0,0) = 'a1')
                    new_pos = self.board.convert_coordinates_to_position((new_x, new_y))
                    
                    while new_pos: # Ensure move is within board boundaries
                        piece_at_new_pos = self.board.get_piece_at_position(new_pos).strip()
                        
                        if piece_at_new_pos == '-':  # Empty square → Movement allowed
                            if (dx, dy) in piece.move_directions:
                                # Format: (<piece to be moved>, <current piece position>, <new position after move>)
                                moves.append((self.board.colour + piece.name, position, new_pos))
                        else: # There is a piece at the new position  
                            # Opponent's piece for capture 
                            if (dx, dy) in piece.capture_directions and piece_at_new_pos[0] != self.board.colour:
                                moves.append((self.board.colour + piece.name, position, new_pos))  # Capture
                            break # After capture, piece cannot move any further in that direction
                        
                        # Stop if it's a capture or single-step piece (like a King)
                        # If the piece is a single step (only one move in each direction), 
                        # Or if the current direction is a capture direction, and single_step_capture is True, 
                        # It stops further movement in that direction.
                        if piece.single_step_movement or ((dx, dy) in piece.capture_directions and piece.single_step_capture):
                            break  

                        # Update the new coordinates and board position in the next direction if single_step_movement=False
                        new_x += dx
                        new_y += dy
                        new_pos = self.board.convert_coordinates_to_position((new_x, new_y))
   
            return moves

        # Return a concatenated list of all the moves for each piece on the board
        return list(chain.from_iterable(generate_moves(piece) for piece in pieces))

    
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
                for (x, y), piece in new_board.board.items():  
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
        # NOTE: contagion of x's zombies happens after the end of the x's turn.
        # ex: if w moves their zombie up a square, at the end of w's turn it will infect any piece around it (as specified),
        # those new w zombies will only keep infecting after the end of w's next turn
        # the only exception is if a Peon get's promoted (to a zombie) (by moving to the end file or being flung), it will not infect at the end of that turn, only at the end of the next turn 
        
        return new_board