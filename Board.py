import sys

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
        
        # Read remaining board input (excluding last 3 lines, not including empty last line)
        lines = sys.stdin.readlines()[:-2]  # Removes the last 3 lines

        # Process each line in board.txt
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 2:
                square, piece = parts
                square = square[:-1] # remove trailing ':'
                piece = piece[:-2].strip("'") # remove quotations and trailing ','
                if square in Board.position_map:
                    self.board[Board.position_map[square]] = piece + '\t'  # Assign piece to board coordinate


    def __str__(self):
        # return a string representation of the board 8x8 with row and col titles
        board_representation = ""
        for j in range(7, -1, -1):  # Print from rank 8 to 1 (top to bottom)
            board_representation += str(j + 1) + "\t" + " ".join(self.board[(i, j)] for i in range(8)) + "\n"
        board_representation += "\ta\t b\t c\t d\t e\t f\t g\t h\n"
        return board_representation
    
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
