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

        # Directionality for Peons
        direction = ["Up","Forward"] if self.board.colour == 'w' else ["Down","Backward"]  # White moves up, Black moves down

        # Define pieces with their name, move_directions, capture_directions, single_step_movement, single_step_capture
        # TODO: Reorder the pieces from most important to least so that the order of the moves is more efficient for A4
        pieces = [
            Piece('K', Piece.Movements["8-Square"], single_step_capture=True, single_step_movement=True),
            Piece('B', Piece.Movements["Diagonals"]),
            Piece('R', Piece.Movements["Straight-Files"]),
            Piece('Q', Piece.Movements["8-Square"]),
            Piece('N', Piece.Movements["L-Shape"], single_step_capture=True, single_step_movement=True),
            Piece('P', Piece.Movements[f"{direction[0]}-1"], capture_directions=Piece.Movements[f"Diagonal-{direction[1]}"], single_step_capture=True, single_step_movement=True),
            Piece('Z', Piece.Movements["Straight-Files"], single_step_capture=True, single_step_movement=True),
            Piece('C', Piece.Movements["Straight-Files"], capture_directions=[], single_step_movement=True),
            Piece('F', Piece.Movements["8-Square"], capture_directions=[], single_step_movement=True),
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
        """
        Generates board files for each valid move and removes old board files.
        This function performs the following steps:
            1. Removes old board files in the current directory that match the pattern "board.xxx".
            2. Retrieves a list of valid moves.
            3. For each valid move, generates a new board configuration.
            4. Saves the new board configuration to a file named in the format "board.xxx", where "xxx" is a zero-padded counter.
            The board file contains:
                - The board's colour and three integer values.
                - A dictionary of board positions and their corresponding pieces.
                - Three final lines with the values "0 0 0".
            The board files are saved in the current directory.
        """

        if self.is_checkmate():
            print("It is the end of the game, you already won, good job! :)")
            return

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
        """
        Generates a new board state after applying a given move.
        This method creates a deep copy of the current board state and applies the specified move to generate a new board state.
        It also handles special rules and conditions such as contagion of zombies, promotion of pawns to zombies, and switching turns.
        Args:
            move (tuple): A tuple containing the piece to be moved, its current position, and its new position.
        Returns:
            Board: A new board object representing the state of the board after the move has been applied.
        TODO:
            - Implement the necessary chess rules (http://www.uschess.org/content/view/7324) (not required for this assignment)
        """

        # modify the board state after applying the move.

        new_board = copy.deepcopy(self.board)  # Deep copy to avoid modifying the original board
        piece, pos, new_pos = move

        '''
        # TODO: Implement the necessary chess rules (http://www.uschess.org/content/view/7324):
            1. If King is in check, only three ways out:
                a. King moves out of check
                b. Piece captures the threat
                c. Blocking the check 
            2. King cannot put himself into a check
            3. Types of draws:
                a. Insufficient mating material. 
                b. Stalemate
                c. Three move repetition
                d. Both players run out of time
                4. 50 Move rule
        ''' 
        
        new_board.board[Board.position_map[pos]] = '-\t' # empty square where the piece used to be
        new_board.board[Board.position_map[new_pos]] = piece + '\t' # square where the piece is moving to is overwritten (either a simple movement of the piece or an opponent capture)

        '''
        NOTE: contagion of x's zombies happens after the end of the x's turn.
        ex: if w moves their zombie up a square, at the end of w's turn it will infect any piece around it (Piece.Movements["Straight-Files"]),
        those new w zombies will only keep infecting after the end of w's next turn
        the only exception is if a Peon get's promoted (to a zombie) (by moving to the end file or being flung), 
        it will not infect at the end of that turn, only at the end of the next turn 
        '''
        new_board.contagion()
       
        # Promote Peon's on the last rank into Zombies
        new_board.promotion()
        
        new_board.switch_turn()
        return new_board
    
    def is_checkmate(self):
        """
        Determines if the current player is in a checkmate position.
        Checkmate occurs when the opposing King is captured.
        Returns:
            bool: True if the current player is in checkmate, False otherwise.
        """
        # Get the position of the opposing King
        opposing_king = 'wK' if self.board.colour == 'b' else 'bK'
        king_position = self.board.get_piece_positions(opposing_king)

        # If the opposing King is not on the board, it's checkmate
        if not king_position:
            return True

        return False