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
        return str(self.board)
    
    def valid_moves(self):
        def moves_flinger():
            moves = ["flinger"]
            
            return moves
            
        def moves_peon():
            moves = ["peon"]
            
            return moves

        def moves_knight():
            moves = ["knight"]
            
            return moves
        
        def moves_cannon():
            moves = ["cannon"]
            
            return moves
        
        def moves_queen():
            moves = ["queen"]
            
            return moves
        
        def moves_king():
            moves = ["king"]
            
            return moves
        
        def moves_zombie():
            moves = ["zombie"]
            
            return moves
        
        def moves_bishop():
            moves = ["bishop"]
            
            return moves
        
        def moves_rook():
            moves = ["rook"]
            
            return moves
        
        move_functions = [moves_flinger, moves_peon, moves_knight, moves_cannon, 
                      moves_queen, moves_king, moves_zombie, moves_bishop, moves_rook]

        moves = list(chain.from_iterable(func() for func in move_functions))
        return moves