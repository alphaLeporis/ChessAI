import chess
from project.chess_utilities.utility import Utility


class ExampleUtility(Utility):

    def __init__(self) -> None:
        pass

    # Calculate the amount of white pieces minus the amount of black pieces    
    def board_value(self, board: chess.Board):
        n_white = 0
        n_white += len(board.pieces(piece_type=chess.PAWN, color=chess.WHITE)) * 10
        n_white += len(board.pieces(piece_type=chess.BISHOP, color=chess.WHITE)) * 40
        n_white += len(board.pieces(piece_type=chess.KNIGHT, color=chess.WHITE)) * 40
        n_white += len(board.pieces(piece_type=chess.ROOK, color=chess.WHITE)) * 50
        n_white += len(board.pieces(piece_type=chess.QUEEN, color=chess.WHITE)) * 100

        n_black = 0
        n_black += len(board.pieces(piece_type=chess.PAWN, color=chess.BLACK)) * 10
        n_black += len(board.pieces(piece_type=chess.BISHOP, color=chess.BLACK)) * 40
        n_black += len(board.pieces(piece_type=chess.KNIGHT, color=chess.BLACK)) * 40
        n_black += len(board.pieces(piece_type=chess.ROOK, color=chess.BLACK)) * 50
        n_black += len(board.pieces(piece_type=chess.QUEEN, color=chess.BLACK)) * 100
        return n_white - n_black
