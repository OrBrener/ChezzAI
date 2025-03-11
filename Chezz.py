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
            if isinstance(move[2], list):
                if move[2][0] == "Cannonball":
                    return_str += f"{num_moves+1}\t{move[2][0]} from {move[1]} going {Piece.directions[move[2][1]]}!\n"
                elif move[2][0].startswith("Flung"):
                    return_str += f"{num_moves+1}\t{move[0][1]} on {move[1]} Flung to {move[2][1]}"
                    if move[2][0] == "Flung-Shattered":
                        return_str += " Shattered!"
                    return_str += "\n"
            else:
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
        
        def cannon_moves():
            """
            Generate all possible moves for the Cannon piece on the board.
            The Cannon piece has two types of moves:
            1. Movement: The Cannon can move to any empty square in its move directions.
            2. Cannonball: The Cannon can shoot a cannonball in its diagonal directions and destroy all pieces in it's path.
                Note: it cannot shoot a cannonball that does not destroy any pieces (null move)
            Returns:
                list: A list of tuples representing the possible moves for the Cannon piece.
                      Each tuple is in the format:
                      (<piece to be moved>, <current piece position>, <new position after move>)
                      or
                      (<piece to be moved>, <current piece position>, ["Cannonball", (dx, dy)]) 
                      Where (dx, dy) are the coordinates in which the cannonball will be moving
            """

            moves = []
            cannon_piece = next(piece for piece in pieces if piece.name == 'C')
            name, move_directions = cannon_piece.name, cannon_piece.move_directions
            
            for position in self.board.get_piece_positions(self.board.colour + name):
                x, y = self.board.get_coordinates_at_position(position) # Convert chess notation to (row, col)
                
                # Movement of Cannon
                for dx, dy in move_directions:  
                    new_x, new_y = x + dx, y + dy
                    # Convert coordinates to board position (ex: (0,0) = 'a1')
                    new_pos = self.board.convert_coordinates_to_position((new_x, new_y))
                    
                    if new_pos: # Ensure move is within board boundaries
                        piece_at_new_pos = self.board.get_piece_at_position(new_pos).strip()
                        if piece_at_new_pos == '-':  # Empty square → Movement allowed
                            # Format: (<piece to be moved>, <current piece position>, <new position after move>)
                            moves.append((self.board.colour + name, position, new_pos))
                
                # Cannonball
                for dx, dy in Piece.Movements["Diagonals"]:
                    new_x, new_y = x + dx, y + dy
                    # Convert coordinates to board position (ex: (0,0) = 'a1')
                    new_pos = self.board.convert_coordinates_to_position((new_x, new_y))

                    while new_pos: # Ensure move is within board boundaries
                        piece_at_new_pos = self.board.get_piece_at_position(new_pos).strip()
                        if piece_at_new_pos != '-':  # There is a piece → cannonball allowed
                            # Format: (<piece to be moved>, <current piece position>, ["Cannonball", (dx, dy)]) 
                            # Where (dx, dy) are the coordinates in which the cannonball will be moving
                            moves.append((self.board.colour + name, position, ["Cannonball", (dx,dy)]))
                            break

                        # Update the new coordinates and board position in the next direction
                        new_x += dx
                        new_y += dy
                        new_pos = self.board.convert_coordinates_to_position((new_x, new_y))
               
            return moves
        
        def flinger_moves():
            """
            Generate all possible moves for the 'Flinger' piece on the board.
            The function calculates both the standard moves and the special 'flinging' moves
            for the 'Flinger' piece. The 'Flinger' can move to adjacent squares and can also
            fling other pieces in the 8-square directions.
            Returns:
                list: A list of tuples representing possible moves. Each tuple contains:
                    - The piece to be moved (str)
                    - The current position of the piece (str)
                    - The new position after the move (str) or a list indicating a special move
                      (e.g., ["Flung", new_pos] or ["Flung-Shattered", new_pos])
            """

            moves = []
            flinger_piece = next(piece for piece in pieces if piece.name == 'F')
            name, move_directions = flinger_piece.name, flinger_piece.move_directions
            
            for position in self.board.get_piece_positions(self.board.colour + name):
                x, y = self.board.get_coordinates_at_position(position) # Convert chess notation to (row, col)

                # Movement of Flinger
                for dx, dy in move_directions:  
                    new_x, new_y = x + dx, y + dy
                    # Convert coordinates to board position (ex: (0,0) = 'a1')
                    new_pos = self.board.convert_coordinates_to_position((new_x, new_y))
                    
                    if new_pos: # Ensure move is within board boundaries
                        piece_at_new_pos = self.board.get_piece_at_position(new_pos).strip()
                        if piece_at_new_pos == '-':  # Empty square → Movement allowed
                            # Format: (<piece to be moved>, <current piece position>, <new position after move>)
                            moves.append((self.board.colour + name, position, new_pos))
                
                # Flinging
                for dx, dy in Piece.Movements["8-Square"]:
                    flung_piece_cords = (x - dx, y - dy)
                    new_x, new_y = x + dx, y + dy
                    # Convert coordinates to board position (ex: (0,0) = 'a1')
                    new_pos = self.board.convert_coordinates_to_position((new_x, new_y))
                    flung_piece_pos = self.board.convert_coordinates_to_position((flung_piece_cords))
                    if flung_piece_pos: # if there is a piece to be flung
                        flung_piece = self.board.get_piece_at_position(flung_piece_pos).strip()
                        if flung_piece != '-' and flung_piece[0] == self.board.colour: # Make sure to flinging pieces of the same colour 
                            while new_pos: # Ensure move is within board boundaries
                                piece_at_new_pos = self.board.get_piece_at_position(new_pos).strip()
                                if piece_at_new_pos == '-': # Flinging a piece to an empty square
                                    moves.append((flung_piece, flung_piece_pos, ["Flung", new_pos]))
                                elif piece_at_new_pos[0] != self.board.colour: # Flinging a piece onto an opponent's piece, shattering both
                                    if piece_at_new_pos[1] != 'K': # Cannot fling onto an opponent's King
                                        moves.append((flung_piece, flung_piece_pos, ["Flung-Shattered", new_pos]))

                                # Update the new coordinates and board position in the next direction
                                new_x += dx
                                new_y += dy
                                new_pos = self.board.convert_coordinates_to_position((new_x, new_y))
            return moves

        # Return a concatenated list of all the moves for each piece on the board
        return list(chain.from_iterable(generate_moves(piece) for piece in pieces if piece.name not in ['C', 'F'])) + cannon_moves() + flinger_moves()

    
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
        """

        # modify the board state after applying the move.

        new_board = copy.deepcopy(self.board)  # Deep copy to avoid modifying the original board
        piece, pos, new_pos = move

        # Special case for Cannon and Flinger
        if isinstance(new_pos, list):
            if new_pos[0] == "Cannonball":
                self.cannonball_move(pos, new_pos[1], new_board)
            elif new_pos[0] == "Flung": # Piece is flung to an empty square
                new_board.board[Board.position_map[pos]] = '-\t' # empty square where the piece used to be
                new_board.board[Board.position_map[new_pos[1]]] = piece + '\t' # square where the piece is flung to
            elif new_pos[0] == "Flung-Shattered": # Piece is flung to an enemy square and both are shattered
                new_board.board[Board.position_map[pos]] = '-\t' # empty square where the piece used to be
                new_board.board[Board.position_map[new_pos[1]]] = '-\t' # empty square to where it is flung -- both pieces are shattered
        # All other regular movements and captures
        else:        
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
    
    def cannonball_move(self, pos, new_pos, new_board):
        # Method to handle the movement of a cannonball piece on the chessboard
            """
            Moves a cannonball piece from the current position to a new position on the board.

            Parameters:
            pos (str): The current position of the cannonball in chess notation (e.g., 'a1').
            new_pos (tuple): A tuple containing the direction of the move as (dx, dy).
            new_board (Board): The board object representing the current state of the game.

            Returns:
            None
            """
            x, y = self.board.get_coordinates_at_position(pos) # Convert chess notation to (row, col)
            dx, dy = new_pos
            new_x, new_y = x + dx, y + dy
            # Convert coordinates to board position (ex: (0,0) = 'a1')
            cannon_pos = self.board.convert_coordinates_to_position((new_x, new_y))

            while cannon_pos: # Ensure move is within board boundaries
                new_board.board[Board.position_map[cannon_pos]] = '-\t' # Cannon destroys all pieces in it's path
                
                # Update the coordinates until the end of the board
                new_x += dx
                new_y += dy
                cannon_pos = self.board.convert_coordinates_to_position((new_x, new_y))
    
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