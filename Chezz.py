from Board import *

class Chezz:
    def __init__(self, board=None, board_file=None, time_used=0, time_allowed=60000, num_moves=0):
        self.board = Board() # initialize a starting position board
        if board: # if a board is passed in, use that board
            self.board = board
        else: # if no board is passed in, populate the board with the given board file
            if board_file:
                self.board.populate_board(board_file)
        self.time_used = self.board.time_used
        self.time_allowed = self.board.time_allowed
        self.num_moves = self.board.num_moves

    def __str__( self ):
        # return a string representation of the current state of the board and all the valid moves
        return_str = f"Time used: {self.time_used}\nTime allowed: {self.time_allowed}\nNumber of moves: {self.num_moves}\n"
        return_str += str(self.board)
        
        return_str += "Moves: \n"
        num_moves = 0
        for move in self.get_legal_moves():
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
    
    def get_legal_moves(self, get_first = None):

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
                                
                                # If I only want to return the first move
                                if get_first:
                                    return moves
                                
                        else: # There is a piece at the new position  
                            # Opponent's piece for capture 
                            if (dx, dy) in piece.capture_directions and piece_at_new_pos[0] != self.board.color:
                                moves.append((self.board.color + piece.name, position, new_pos))  # Capture
                                
                                # If I only want to return the first move
                                if get_first:
                                    return moves
                                
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
        
        # If get_first is True, return the first valid move found
        if get_first:
            for piece in pieces.values():
                moves = generate_moves(piece)
                if moves:
                    return moves
            # If no moves found for Q, Z, R, K, N, B, P
            return flinger_moves() + cannon_moves
        
        # Return a concatenated list of all the moves for each piece on the board
        return generate_moves(pieces['Q']) + flinger_moves() + generate_moves(pieces['Z']) + cannon_moves() + generate_moves(pieces['R']) + generate_moves(pieces['K']) + generate_moves(pieces['N']) + generate_moves(pieces['B']) + generate_moves(pieces['P'])
    
    def is_checkmate(self, opponent=False):
        """
        Determines if the current player (or opponent) is in a checkmate position.
        Checkmate occurs when the King is captured.
        Returns:
            bool: True if the player is in checkmate, False otherwise.
        """
        opposing_king = 'wK' if self.board.color == 'b' else 'bK'
        if opponent:
            king_position = self.board.get_piece_positions(opposing_king)
        else:
            king_position = self.board.get_piece_positions(self.board.color + 'K')

        # If the King is not on the board, it's checkmate
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

        # Check white or black checkmate
        if not board.get_piece_positions('wK'):
            return -10000000
        if not board.get_piece_positions('bK'):
            return 10000000
        
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
        
        piece_value = [0,0]
        center_control = [0,0]
        king_safety = [0,0]
        pawn_promotion = [0,0]
        num_zombies = [0,0]
        zombie_contagion = [0,0]
        unmotivated_pieces = [0,0]
        dist_king = [0,0]
        pin = [0,0]
        fork = [0,0]

        piece_values = {
            'P': 1, 'N': 4, 'B': 3, 'R': 5, 'Q': 20, 'K': 1000, 'Z': 10, 'C': 10, 'F': 15
        }

        # Count the number of pieces not in their original positions
        original_positions = {
            'wP': ['a2', 'b2', 'c2', 'd2', 'f2', 'g2', 'h2'],
            'bP': ['a7', 'b7', 'c7', 'd7', 'f7', 'g7', 'h7'],
            'wR': ['h1'],
            'bR': ['h8'],
            'wN': ['b1', 'g1'],
            'bN': ['b8', 'g8'],
            'wB': ['f1'],
            'bB': ['f8'],
            'wQ': ['d1'],
            'bQ': ['d8'],
            'wK': ['e1'],
            'bK': ['e8'],
            'wZ': ['e2'],
            'bZ': ['e7'],
            'wC': ['c1'],
            'bC': ['c8'],
            'wF': ['a1'],
            'bF': ['a8']
        }

        for piece_key in original_positions:
            piece_color = piece_key[0]
            for position in board.get_piece_positions(piece_key):
                if piece_key in original_positions and position not in original_positions[piece_key]:
                    if piece_color == 'w':
                        unmotivated_pieces[0] += 1  # Reward for moving pieces from their original positions
                    else:
                        unmotivated_pieces[1] += 1  # Penalize opponent's pieces moving from their original positions

        for (x, y), piece in board.board.items():
            if piece.strip() != '-':
                piece_type = piece.strip()[1]
                piece_color = piece.strip()[0]

                if piece_color == 'w':
                    piece_value[0] += piece_values[piece_type]
                else:
                    piece_value[1] += piece_values[piece_type]

                
                # Control of the center
                center_squares = [(2, 4), (3, 4), (4, 4), (2, 3), (3, 3), (4, 3)]
                if (x, y) in center_squares:
                    if piece_color == 'w':
                        center_control[0] += 1
                        if piece_type == 'Z':
                            center_control[0] += 9
                    else:
                        center_control[1] += 1
                        if piece_type == 'Z':
                            center_control[1] += 9

                # King safety: Check how many friendly pieces are protecting the king
                if piece_type == 'K':
                    for dx, dy in pieces['K'].move_directions:
                        new_x, new_y = x + dx, y + dy
                        adjacent_pos = board.convert_coordinates_to_position((new_x, new_y))
                        if adjacent_pos:  # Ensure move is within board boundaries
                            piece_at_adjacent = board.get_piece_at_position(adjacent_pos).strip()
                            if piece_at_adjacent != '-' and piece_at_adjacent[0] == piece_color:
                                if piece_color == 'w':
                                    king_safety[0] += 1
                                else:
                                    king_safety[0] += 1

                # Check if the pawn is getting closer to the final rank for promotion
                if piece_type == 'P':
                   # Incentivize Peon moving forward: each move forward is worth 1 extra point (a1 = 0, a2 = 1, a3 = 2, etc)
                    if piece_color == 'w':
                        pawn_promotion[0] += y  # Reward for white pawn moving forward
                    else:
                        pawn_promotion[1] += (7 - y)  # Penalize black pawn moving forward

                # Queen on the same horizontal or diagonal as the King
                if piece_type == 'Q':
                    king_positions = board.get_piece_positions('bK') if piece_color == 'w' else board.get_piece_positions('wK')
                    if king_positions:
                        king_x, king_y = board.get_coordinates_at_position(king_positions[0])
                        if x == king_x or y == king_y or abs(x - king_x) == abs(y - king_y):
                            distance = max(abs(x - king_x), abs(y - king_y))
                            bonus = 6 - distance  # Closer to the king gets a higher bonus
                            if piece_color == 'w':
                                dist_king[0] += 5 + bonus
                            else:
                                dist_king[1] += 5 + bonus

                # Rook on the same horizontal or vertical as the King
                if piece_type == 'R':
                    king_positions = board.get_piece_positions('bK') if piece_color == 'w' else board.get_piece_positions('wK')
                    if king_positions:
                        king_x, king_y = board.get_coordinates_at_position(king_positions[0])
                        if x == king_x or y == king_y:
                            distance = abs(x - king_x) + abs(y - king_y)
                            bonus = 6 - distance  # Closer to the king gets a higher bonus
                            if piece_color == 'w':
                                dist_king[0] += 5 + bonus
                            else:
                                dist_king[1] += 5 + bonus

                # Bishop on the same diagonal as the King
                if piece_type == 'B':
                    king_positions = board.get_piece_positions('bK') if piece_color == 'w' else board.get_piece_positions('wK')
                    if king_positions:
                        king_x, king_y = board.get_coordinates_at_position(king_positions[0])
                        if abs(x - king_x) == abs(y - king_y):  # Same diagonal
                            distance = abs(x - king_x)
                            bonus = 6 - distance  # Closer to the king gets a higher bonus
                            if piece_color == 'w':
                                dist_king[0] += 5 + bonus
                            else:
                                dist_king[1] += 5 + bonus

                # Knight on the same L-shape path as the King
                if piece_type == 'N':
                    king_positions = board.get_piece_positions('bK') if piece_color == 'w' else board.get_piece_positions('wK')
                    if king_positions:
                        king_x, king_y = board.get_coordinates_at_position(king_positions[0])
                        for dx, dy in Piece.Movements["L-Shape"]:
                            if x + dx == king_x and y + dy == king_y:
                                bonus = 6  # Fixed bonus for being in an L-shape path to the King
                                if piece_color == 'w':
                                    dist_king[0] += 5 + bonus
                                else:
                                    dist_king[1] += 5 + bonus

                # Check for pinning
                if piece_type in ['R', 'B', 'Q', 'C']:
                    king_positions = board.get_piece_positions('bK') if piece_color == 'w' else board.get_piece_positions('wK')
                    if king_positions:
                        king_x, king_y = board.get_coordinates_at_position(king_positions[0])
                        dx, dy = king_x - x, king_y - y
                        if dx == 0 or dy == 0 or abs(dx) == abs(dy):  # Same row, column, or diagonal
                            step_x, step_y = (dx // abs(dx) if dx != 0 else 0, dy // abs(dy) if dy != 0 else 0)
                            intermediate_x, intermediate_y = x + step_x, y + step_y
                            pinned = True
                            while (intermediate_x, intermediate_y) != (king_x, king_y):
                                intermediate_pos = board.convert_coordinates_to_position((intermediate_x, intermediate_y))
                                if intermediate_pos:
                                    piece_at_intermediate = board.get_piece_at_position(intermediate_pos).strip()
                                    if piece_at_intermediate != '-':
                                        pinned = False
                                        break
                                intermediate_x += step_x
                                intermediate_y += step_y
                            if pinned:
                                if piece_color == 'w':
                                    pin[0] += 10  # Reward for pinning opponent's pieces
                                else:
                                    pin[1] += 10  # Penalize for being pinned

                # Check for forking
                if piece_type in ['N', 'Q', 'B', 'P', 'Z', 'C']:
                    king_positions = board.get_piece_positions('bK') if piece_color == 'w' else board.get_piece_positions('wK')
                    if king_positions:
                        king_x, king_y = board.get_coordinates_at_position(king_positions[0])
                        forked_pieces = 0
                        move_directions = pieces[piece_type].capture_directions
                        for dx, dy in move_directions:
                            new_x, new_y = x + dx, y + dy
                            fork_pos = board.convert_coordinates_to_position((new_x, new_y))
                            if fork_pos:
                                piece_at_fork = board.get_piece_at_position(fork_pos).strip()
                                if piece_at_fork != '-' and piece_at_fork[0] != piece_color:
                                    forked_pieces += 1
                        if forked_pieces >= 2:
                            if piece_color == 'w':
                                fork[0] += 15  # Reward for forking multiple valuable pieces
                            else:
                                fork[1] += 15  # Penalize for being forked

                # Incentivize Knight moving to the center
                if piece_type == 'N':
                    if (x, y) in center_squares:
                        if piece_color == 'w':
                            center_control[0] += 2
                        else:
                            center_control[1] += 2
                # Zombie contagion: Evaluate potential for zombies to convert enemy pieces
                if piece_type == 'Z':
                    # Count the number of zombies on the board
                    if piece_color == 'w':
                        num_zombies[0] += 1
                    else: 
                        num_zombies[1] += 1
                    for dx, dy in pieces['Z'].move_directions:
                        new_x, new_y = x + dx, y + dy
                        adjacent_pos = board.convert_coordinates_to_position((new_x, new_y))
                        if adjacent_pos: # Ensure move is within board boundaries
                            piece_at_adjacent = board.get_piece_at_position(adjacent_pos).strip()
                            if piece_at_adjacent != '-': # Not an empty space
                                # Contagion does not effect your own pieces or Kings or other Zombies
                                if piece_at_adjacent[0] != piece_color and piece_at_adjacent[1] not in ['K','Z']:
                                    if piece_color == 'w':
                                        zombie_contagion[0] += 1
                                    else:
                                        zombie_contagion[1] += 1

                # TODO: no need to capture a piece with a zombie since it will infect the piece anyways unless it is an opponents piece or a king
        
                '''
                # TODO: better heuristic is to incentivize certain moves for pieces;
                # ex: Peon moving forward: each move forward is worth 1 extra point (a1 = 0, a2 = 1, a3 = 2, etc)
                # ex: Knight moving to the center: each move to the center is worth 2 extra points
                # ex: Queen on the same horizontal or diagonal as the King: 5 extra points 
                # (maybe the closer it is to the king it gets a bonus +1 (6 squares away), +2 (5 squares away) etc. ) 
                '''      
                
        # # Combine all factors into the final heuristic value
        heuristic_value =  ( 10 * (piece_value[0] - piece_value[1])) + ((unmotivated_pieces[0] - unmotivated_pieces[1]))  + ( 2 * (center_control[0] - center_control[1])) + \
                                ((king_safety[0] - king_safety[1])) + ((pawn_promotion[0] - pawn_promotion[1])) + ( 5 * (dist_king[0] - dist_king[1])) + \
                                ( 2 * (pin[0] - pin[1])) + ( 3 * (fork[0] - fork[1]))+ ( 2 * (num_zombies[0] - num_zombies[1])) + \
                                ( 2 * (zombie_contagion[0] - zombie_contagion[1]))
        # TODO: make the heuristic the same value regardless of the color (positive for white advantage, negative for black advantage)
        if board.color == 'b':
            return -heuristic_value
        else:
            return heuristic_value
            
    def max_score( self, currentState, depth, alpha=-10000000, beta=10000000):
        if depth == 0:
            return currentState.heuristic( currentState.board ), None
        
        bestScore = -10000000

        successors = currentState.get_legal_moves()
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
            return currentState.heuristic( currentState.board ), None
        
        worstScore = 10000000

        successors = currentState.get_legal_moves()
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