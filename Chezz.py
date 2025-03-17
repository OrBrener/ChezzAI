from Board import *

class Chezz:
    def __init__(self, board=None, time_used=0, time_allowed=60000, num_moves=0):
        if board:
            self.board = board
        else: 
            self.board = Board()
            self.board.populate_board()
        self.time_used = self.board.time_used
        self.time_allowed = self.board.time_allowed
        self.num_moves = self.board.num_moves

    def __str__( self ):
        # return a string representation of the current state of the board and all the valid moves
        return_str = f"Time used: {self.time_used}\nTime allowed: {self.time_allowed}\nNumber of moves: {self.num_moves}\n"
        return_str += str(self.board)
        
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
        direction = ["Up","Forward"] if self.board.color == 'w' else ["Down","Backward"]  # White moves up, Black moves down

        # Define pieces with their name, move_directions, capture_directions, single_step_movement, single_step_capture
        pieces = {
            'Q': Piece('Q', Piece.Movements["8-Square"]),
            'F': Piece('F', Piece.Movements["8-Square"], capture_directions=[], single_step_movement=True),
            'Z': Piece('Z', Piece.Movements["Straight-Files"], single_step_capture=True, single_step_movement=True),
            'C': Piece('C', Piece.Movements["Straight-Files"], capture_directions=[], single_step_movement=True),
            'R': Piece('R', Piece.Movements["Straight-Files"]),           
            'K': Piece('K', Piece.Movements["8-Square"], single_step_capture=True, single_step_movement=True),
            'N': Piece('N', Piece.Movements["L-Shape"], single_step_capture=True, single_step_movement=True),
            'B': Piece('B', Piece.Movements["Diagonals"]),
            'P': Piece('P', Piece.Movements[f"{direction[0]}-1"], capture_directions=Piece.Movements[f"Diagonal-{direction[1]}"], single_step_capture=True, single_step_movement=True),
        }

        def generate_moves(piece):
            '''
            Returns a list of moves (piece movement to an empty square, or a piece capture) 
            for all of the instances of the given piece on the current board
            '''
            # TODO: Reorder the move appends to captures before simple movement so that the order of the moves is more efficient for A4
            moves = []

            # Get all positions of the given piece type
            for position in self.board.get_piece_positions(self.board.color + piece.name):
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
                                moves.append((self.board.color + piece.name, position, new_pos))
                        else: # There is a piece at the new position  
                            # Opponent's piece for capture 
                            if (dx, dy) in piece.capture_directions and piece_at_new_pos[0] != self.board.color:
                                moves.append((self.board.color + piece.name, position, new_pos))  # Capture
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
            cannon_piece = pieces['C']
            name, move_directions = cannon_piece.name, cannon_piece.move_directions
            
            for position in self.board.get_piece_positions(self.board.color + name):
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
                            moves.append((self.board.color + name, position, new_pos))
                
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
                            moves.append((self.board.color + name, position, ["Cannonball", (dx,dy)]))
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
            flinger_piece = pieces['F']
            name, move_directions = flinger_piece.name, flinger_piece.move_directions
            
            for position in self.board.get_piece_positions(self.board.color + name):
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
                            moves.append((self.board.color + name, position, new_pos))
                
                # Flinging
                for dx, dy in Piece.Movements["8-Square"]:
                    flung_piece_cords = (x - dx, y - dy)
                    new_x, new_y = x + dx, y + dy
                    # Convert coordinates to board position (ex: (0,0) = 'a1')
                    new_pos = self.board.convert_coordinates_to_position((new_x, new_y))
                    flung_piece_pos = self.board.convert_coordinates_to_position((flung_piece_cords))
                    if flung_piece_pos: # if there is a piece to be flung
                        flung_piece = self.board.get_piece_at_position(flung_piece_pos).strip()
                        if flung_piece != '-' and flung_piece[0] == self.board.color: # Make sure to flinging pieces of the same colour 
                            while new_pos: # Ensure move is within board boundaries
                                piece_at_new_pos = self.board.get_piece_at_position(new_pos).strip()
                                if piece_at_new_pos == '-': # Flinging a piece to an empty square
                                    moves.append((flung_piece, flung_piece_pos, ["Flung", new_pos]))
                                elif piece_at_new_pos[0] != self.board.color: # Flinging a piece onto an opponent's piece, shattering both
                                    if piece_at_new_pos[1] != 'K': # Cannot fling onto an opponent's King
                                        moves.append((flung_piece, flung_piece_pos, ["Flung-Shattered", new_pos]))

                                # Update the new coordinates and board position in the next direction
                                new_x += dx
                                new_y += dy
                                new_pos = self.board.convert_coordinates_to_position((new_x, new_y))
            return moves

        # Return a concatenated list of all the moves for each piece on the board
        return generate_moves(pieces['Q']) + flinger_moves() + generate_moves(pieces['Z']) + cannon_moves() + generate_moves(pieces['R']) + generate_moves(pieces['K']) + generate_moves(pieces['N']) + generate_moves(pieces['B']) + generate_moves(pieces['P'])
    
    def is_checkmate(self):
        """
        Determines if the current player is in a checkmate position.
        Checkmate occurs when the opposing King is captured.
        Returns:
            bool: True if the current player is in checkmate, False otherwise.
        """
        # Get the position of the opposing King
        opposing_king = 'wK' if self.board.color == 'b' else 'bK'
        king_position = self.board.get_piece_positions(opposing_king)

        # If the opposing King is not on the board, it's checkmate
        if not king_position:
            return True

        return False
    
    def heuristic(self, board):
        """
        A heuristic function that evaluates the current board state.
        The heuristic function is used to determine the value of a board state.
        Returns:
            int: The heuristic value of the board state.
        """

        if self.is_checkmate():
            return -1000000
        
        value = 0
        center_control = 0
        pawn_structure = 0
        num_zombies = 0
        zombie_contagion = 0

        def add_piece_value(piece_type):
            piece_values = {
                'P': 1, 'N': 4, 'B': 3, 'R': 5, 'Q': 20, 'K': 1000, 'Z': 30, 'C': 10, 'F': 15
            }
            piece_value = piece_values[piece_type]
            
            if piece_color == board.color:
                return piece_value
            else:
                return -piece_value
        
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        king_positions = {'w': None, 'b': None}
        for (x, y), piece in board.board.items():
            if piece.strip() != '-':
                piece_type = piece.strip()[1]
                piece_color = piece.strip()[0]

                value += add_piece_value(piece_type)
                
                # Control of the center
                if (x, y) in center_squares:
                    if piece_color == board.color:
                        center_control += 1
                    else:
                        center_control -= 1

                # King safety: Track the king's position
                if piece_type == 'K':
                    king_positions[piece_color] = (x, y)

                # Pawn structure: Penalize doubled, isolated, and backward pawns
                if piece_type == 'P':
                    if piece_color == board.color:
                        if y > 0 and board.get_piece_at_position(board.convert_coordinates_to_position((x, y-1))).strip() == board.color+'P':
                            pawn_structure -= 0.5  # Doubled pawn
                        if y < 7 and board.get_piece_at_position(board.convert_coordinates_to_position((x, y+1))).strip() == board.color+'P':
                            pawn_structure -= 0.5  # Doubled pawn
                        if x > 0 and board.get_piece_at_position(board.convert_coordinates_to_position((x-1, y))).strip() != board.color+'P' and board.get_piece_at_position(board.convert_coordinates_to_position((x-1, y))).strip() != '-':
                            pawn_structure -= 0.5  # Isolated pawn
                        if x < 7 and board.get_piece_at_position(board.convert_coordinates_to_position((x+1, y))).strip() != board.color+'P' and board.get_piece_at_position(board.convert_coordinates_to_position((x+1, y))).strip() != '-':
                            pawn_structure -= 0.5  # Isolated pawn


                # Zombie contagion: Evaluate potential for zombies to convert enemy pieces
                if piece_type == 'Z':
                    if piece_color == board.color:
                        # Count the number of zombies on the board
                        num_zombies += 1
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < 8 and 0 <= new_y < 8:
                            adjacent_piece = board.get_piece_at_position(board.convert_coordinates_to_position((new_x, new_y))).strip()
                            if adjacent_piece != '-' and adjacent_piece[0] != piece_color and adjacent_piece[1] != 'K' and adjacent_piece[1] != 'Z':
                                if piece_color == board.color:
                                    zombie_contagion += 1
                                else:
                                    zombie_contagion -= 1

        # # Combine all factors into the final heuristic value
        heuristic_value = value + (num_zombies*10) + (0.5 * center_control) + (0.2 * pawn_structure) + (2 * zombie_contagion)
        return heuristic_value
    
    def max_score( self, currentState, depth, alpha=-10000000, beta=10000000):
        if depth == 0:
            return currentState.heuristic( currentState.board )
        
        bestScore = -10000000

        successors = currentState.valid_moves()
        bestMove = None
        for move in successors:
            next_state = Chezz(currentState.board.generate_board_after_move( move ))
            score = currentState.min_score( next_state, depth-1, alpha, beta )
            if isinstance(score, tuple):
                score = score[0]
            if score > bestScore:
                bestScore = score
                bestMove = move
            if score > beta:
                return bestScore
            alpha = max( alpha, score )
        return bestScore, bestMove
    
    def min_score( self, currentState, depth, alpha, beta ):
        if depth == 0:
            return currentState.heuristic( currentState.board )
        
        worstScore = 10000000

        successors = currentState.valid_moves()
        worstMove = None
        for move in successors:
            next_state = Chezz(currentState.board.generate_board_after_move( move ))
            score = currentState.max_score( next_state, depth-1, alpha, beta )
            if isinstance(score, tuple):
                score = score[0]
            if score < worstScore:
                worstScore = score
                worstMove = move
            if score > alpha:
                return worstScore
            beta = min( beta, score )
        return worstScore, worstMove