class Piece:

    Movements = {
        "8-Square": [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
        "Diagonals": [(-1, -1), (-1, 1), (1, -1), (1, 1)],
        "Straight-Files": [(-1, 0), (1, 0), (0, -1), (0, 1)],
        "L-Shape": [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)],
        "Up-1": [(0,1)],
        "Down-1": [(0,-1)],
        "Diagonal-Forward": [(-1, 1), (1, 1)],
        "Diagonal-Backward": [(-1, -1), (1, -1)],
    }

    directions = {
        (-1, -1): "SW",
        (-1, 1): "NW",
        (1, -1): "SE",
        (1, 1): "NE"
    }

    def __init__(self, name, move_directions, capture_directions=None, single_step_movement=False, single_step_capture=False):
        """
        Initializes a Piece object with the given attributes.
        Args:
            name (str): The name of the piece.
            move_directions (list): A list of directions the piece can move.
            capture_directions (list, optional): A list of directions the piece can capture. Defaults to move_directions if not provided.
            single_step_movement (bool, optional): Indicates if the piece can only move one step at a time. Defaults to False.
            single_step_capture (bool, optional): Indicates if the piece can only capture one step at a time. Defaults to False.
        """
        
        self.name = name
        self.move_directions = move_directions
        self.capture_directions = capture_directions if capture_directions else move_directions
        self.single_step_movement = single_step_movement
        self.single_step_capture = single_step_capture

    def __repr__(self):
        return f"Piece({self.name})"
