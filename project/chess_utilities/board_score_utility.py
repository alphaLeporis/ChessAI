import chess
from project.chess_utilities.utility import Utility


class ExampleUtility(Utility):

    def __init__(self) -> None:
        pass

    # Calculate the amount of white pieces minus the amount of black pieces    
    def get_piece_val(self, board: chess.Board):
        n_white = 0
        n_white += len(board.pieces(piece_type=chess.PAWN, color=chess.WHITE)) * 10
        n_white += len(board.pieces(piece_type=chess.BISHOP, color=chess.WHITE)) * 30
        n_white += len(board.pieces(piece_type=chess.KNIGHT, color=chess.WHITE)) * 30
        n_white += len(board.pieces(piece_type=chess.ROOK, color=chess.WHITE)) * 50
        n_white += len(board.pieces(piece_type=chess.QUEEN, color=chess.WHITE)) * 90
        n_white += len(board.pieces(piece_type=chess.KING, color=chess.WHITE)) *900

        n_black = 0
        n_black += len(board.pieces(piece_type=chess.PAWN, color=chess.BLACK)) * 10
        n_black += len(board.pieces(piece_type=chess.BISHOP, color=chess.BLACK)) * 30
        n_black += len(board.pieces(piece_type=chess.KNIGHT, color=chess.BLACK)) * 30
        n_black += len(board.pieces(piece_type=chess.ROOK, color=chess.BLACK)) * 50
        n_black += len(board.pieces(piece_type=chess.QUEEN, color=chess.BLACK)) * 90
        n_black += len(board.pieces(piece_type=chess.KING, color=chess.BLACK)) *900
        return n_white - n_black

    def is_favorable_move(board: chess.Board, move: chess.Move) -> bool:
        if move.promotion is not None:
            return True
        if board.is_capture(move) and not board.is_en_passant(move):
            if self.get_piece_val(board.piece_type_at(move.from_square)) < self.get_piece_val(board.piece_type_at(move.to_square)) or len(board.attackers(board.turn, move.to_square)) > len(
                board.attackers(not board.turn, move.to_square)
            ):
                return True
        return False


