from Board import *
from itertools import chain

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