import sys
from Piece import *

class Board():

    # Mapping chessboard positions to coordinates
    position_map = {
        'a8': (0,7), 'b8': (1,7), 'c8': (2,7), 'd8': (3,7), 'e8': (4,7), 'f8': (5,7), 'g8': (6,7), 'h8': (7,7),
        'a7': (0,6), 'b7': (1,6), 'c7': (2,6), 'd7': (3,6), 'e7': (4,6), 'f7': (5,6), 'g7': (6,6), 'h7': (7,6),
        'a6': (0,5), 'b6': (1,5), 'c6': (2,5), 'd6': (3,5), 'e6': (4,5), 'f6': (5,5), 'g6': (6,5), 'h6': (7,5),
        'a5': (0,4), 'b5': (1,4), 'c5': (2,4), 'd5': (3,4), 'e5': (4,4), 'f5': (5,4), 'g5': (6,4), 'h5': (7,4),
        'a4': (0,3), 'b4': (1,3), 'c4': (2,3), 'd4': (3,3), 'e4': (4,3), 'f4': (5,3), 'g4': (6,3), 'h4': (7,3),
        'a3': (0,2), 'b3': (1,2), 'c3': (2,2), 'd3': (3,2), 'e3': (4,2), 'f3': (5,2), 'g3': (6,2), 'h3': (7,2),
        'a2': (0,1), 'b2': (1,1), 'c2': (2,1), 'd2': (3,1), 'e2': (4,1), 'f2': (5,1), 'g2': (6,1), 'h2': (7,1),
        'a1': (0,0), 'b1': (1,0), 'c1': (2,0), 'd1': (3,0), 'e1': (4,0), 'f1': (5,0), 'g1': (6,0), 'h1': (7,0),
    }

    def __init__(self):
        # Initialize an empty chessboard (8x8 grid)
        self.board = { (i, j): '-\t' for i in range(8) for j in range(8) }
        self.colour = 'w'
        self.i1 = '0'
        self.i2 = '60000'
        self.i3 = '0'
    
    def populate_board(self):
        # store board info from stdin board file input

        # first line
        self.colour, self.i1, self.i2, self.i3 = sys.stdin.readline().split()
        
        # Read remaining board input (until closing brackets)
        lines = sys.stdin.readlines()

        # Process each line in board.txt
        for line in lines:
            # closing bracket indicates end of board file
            if (line == '}\n'):
                break
            parts = line.strip().split()
            if len(parts) == 2:
                square, piece = parts
                square = square[:-1] # remove trailing ':'
                piece = piece[:-1].strip("'") # remove quotations
                # all the pieces except for the last one have a comma that needs to be removed
                if len(piece) == 5:
                    piece = piece[:-1].strip(",") # remove trailing ','
                if square in Board.position_map:
                    self.board[Board.position_map[square]] = piece + '\t'  # Assign piece to board coordinate


    def __str__(self):
        # return a string representation of the board 8x8 with row and col titles
        board_representation = ""
        for j in range(7, -1, -1):  # Print from rank 8 to 1 (top to bottom)
            board_representation += str(j + 1) + "\t" + " ".join(self.board[(i, j)] for i in range(8)) + "\n"
        board_representation += "\ta\t b\t c\t d\t e\t f\t g\t h\n"
        return board_representation

    def board_string_to_file(turn, board_string, file_path):
        """
        Converts a valid board string to a corresponding valid board file.
        
        :param board_string: A string representation of the board.
        :param file_path: The path to the output file.
        """
        lines = board_string.strip().split('\n')
        board_lines = lines[:-1]
        col_labels = lines[-1].split()

        # Extract the board configuration
        board_config = []
        for line in board_lines:
            parts = line.split()
            rank = parts[0]
            pieces = parts[1:]
            for file, piece in zip(col_labels, pieces):
                if piece != '-':
                    board_config.append((file + rank, piece))

        # Sort the board configuration
        board_config.sort(key=lambda x: Board.position_map[x[0]])

        # Format the board configuration
        formatted_board_config = [f"  {pos}: '{piece}'" for pos, piece in board_config]

        # Create the board file content
        board_file_content = turn + " 0 60000 0\n{\n" + ",\n".join(formatted_board_config) + "\n}\n"

        # Write to the file
        with open(file_path, 'w') as file:
            file.write(board_file_content)

    def get_piece_at_position(self, pos):
        # return the piece at the given board position
        return self.board[Board.position_map[pos]]
    
    def get_coordinates_at_position(self, pos):
        # return the board coordinates at the given position
        # ex: get_coordinates_at_position('a1') = (0,0)
        return Board.position_map[pos]
    
    def convert_coordinates_to_position(self, cord):
        # convert board coordinates into a board position
        # return an empty string if the board if out of the bounds of the board
        # ex: convert_coordinates_to_position((0,0)) = 'a1' convert_coordinates_to_position((-1,0)) = ''

        x, y = cord
        if x < 0 or y < 0 or x > 7 or y > 7: # out of range
            return '' 
        
        reverse_position_map = {v: k for k, v in Board.position_map.items()} # Reverse the dictionary
        return reverse_position_map[cord]

    def get_piece_positions(self, piece_name):
        # return a list of board positions of the given piece
        reverse_position_map = {v: k for k, v in Board.position_map.items()}  # Reverse the dictionary
        positions = [reverse_position_map[square] for square, piece in self.board.items() if piece.strip() == piece_name]
        return positions
    
    def switch_turn(self):
        # Switches the current turn colour
        self.colour = 'b' if self.colour == 'w' else 'w'

    def promotion(self):
        """
        Promote Peons to Zombies when they reach the last rank.
        """
        
        last_rank = 7 if self.colour == 'w' else 0  # Determine the last rank based on the current player's color
        for i in range(8):
            pos = (i, last_rank)
            piece = self.board[pos].strip()
            if piece == self.colour + 'P':  # Check if the piece is a Peon of the current player
                self.board[pos] = self.colour + 'Z' + '\t'  # Promote to zombie

    def contagion(self):
        """
        Spread the contagion effect of zombie pieces on the board.
        This method iterates through all zombie pieces of the current player's color
        and attempts to convert adjacent enemy pieces into zombies. 
        The conversion does not affect the King or other Zombies.
        Aditionionaly, Peons promoted into Zombies on this turn do not cause contagion.
        """
        
        directions = Piece.Movements["Straight-Files"]

        # For all the zombies in the current board
        for position in self.get_piece_positions(self.colour + 'Z'):
            x, y = self.get_coordinates_at_position(position) # Convert chess notation to (row, col)
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                # Convert coordinates to board position (ex: (0,0) = 'a1')
                adjacent_pos = self.convert_coordinates_to_position((new_x, new_y))
                if adjacent_pos: # Ensure move is within board boundaries
                    piece_at_adjacent = self.get_piece_at_position(adjacent_pos).strip()
                    if piece_at_adjacent != '-': # Not an empty space
                        # Contagion does not effect your own pieces or Kings or other Zombies
                        if piece_at_adjacent[0] != self.colour and piece_at_adjacent[1] not in ['K','Z']:
                            self.board[(new_x, new_y)] = self.colour + 'Z' + '\t' # Contagion!

