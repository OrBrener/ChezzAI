import sys
import copy
import os
import re
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
        Additionally, Peons promoted into Zombies on this turn do not cause contagion.
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
            x, y = self.get_coordinates_at_position(pos) # Convert chess notation to (row, col)
            dx, dy = new_pos
            new_x, new_y = x + dx, y + dy
            # Convert coordinates to board position (ex: (0,0) = 'a1')
            cannon_pos = self.convert_coordinates_to_position((new_x, new_y))

            while cannon_pos: # Ensure move is within board boundaries
                new_board.board[Board.position_map[cannon_pos]] = '-\t' # Cannon destroys all pieces in it's path
                
                # Update the coordinates until the end of the board
                new_x += dx
                new_y += dy
                cannon_pos = self.convert_coordinates_to_position((new_x, new_y))
    
    def remove_old_board_files(self):
            # Get a list of all files in the current directory
            files = os.listdir()
            
            # Define the pattern for board files with exactly three digits after "board."
            pattern = re.compile(r"^board\.\d{3}$")
            
            # Loop through the files and remove those that match the board pattern
            for file in files:
                if pattern.match(file):  # Check if the file matches the pattern "board.xxx"
                    os.remove(file)

    def generate_board_files(self, valid_moves, output_mode='file'):
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
        if output_mode == 'file':
            self.remove_old_board_files()

        board_counter = 0
        for move in valid_moves:
            new_board = self.generate_board_after_move(move)
            
            # Save the new board to a file or print to stdout
            filename = f"board.{str(board_counter).zfill(3)}"  # Name format: board.000, board.001, ...
            board_content = f"{new_board.colour} {new_board.i1} {new_board.i2} {new_board.i3}\n"
            board_content += "{\n"  # Open curly bracket

            # Sort board positions in correct order and write them to file
            piece_entries = []
            for (x, y), piece in new_board.board.items():  
                if piece.strip() != "-":
                    piece_entries.append(f"  {new_board.convert_coordinates_to_position((x,y))}: '{piece.strip()}'")

            # Join all entries with ",\n" and write them
            board_content += ",\n".join(piece_entries) + "\n"
            board_content += "}\n"  # Closing curly bracket

            if output_mode == 'file':
                with open(filename, 'w', encoding="utf-8") as file:
                    file.write(board_content)
            elif output_mode == 'stdout':
                print(board_content)

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

        new_board = copy.deepcopy(self)  # Deep copy to avoid modifying the original board
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

