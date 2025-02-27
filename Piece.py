class Piece:
    def __init__(self, name, move_directions, capture_directions=None, single_step_movement=False, single_step_capture=False, special_abilities=None):
        """
        Initializes a Piece object with the given attributes.
        Args:
            name (str): The name of the piece.
            move_directions (list): A list of directions the piece can move.
            capture_directions (list, optional): A list of directions the piece can capture. Defaults to move_directions if not provided.
            single_step_movement (bool, optional): Indicates if the piece can only move one step at a time. Defaults to False.
            single_step_capture (bool, optional): Indicates if the piece can only capture one step at a time. Defaults to False.
            special_abilities (list, optional): A list of special abilities the piece has. Defaults to an empty list.
        """
        
        self.name = name
        self.move_directions = move_directions
        self.capture_directions = capture_directions if capture_directions else move_directions
        self.single_step_movement = single_step_movement
        self.single_step_capture = single_step_capture
        self.special_abilities = special_abilities if special_abilities else []

    def __repr__(self):
        return f"Piece({self.name})"
