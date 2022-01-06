import chess as chess
import project.chess_helpers.parameters as pa

def get_phase(board):
    """
    Gets the game state of the board as a number
    Low numbers indicate early game
    High numbers indiciate endgame
    """
    if board.is_checkmate():
        return -pa.MATE_SCORE

    pawn_phase = 0
    knight_phase = 1
    bishop_phase = 1
    rook_phase = 2
    queen_phase = 4
    total_phase = 16*pawn_phase + 4*knight_phase + 4*bishop_phase + 4*rook_phase + 2*queen_phase

    phase = total_phase
    phase -= (len(board.pieces(chess.PAWN, chess.WHITE)) + len(board.pieces(chess.PAWN, chess.BLACK))) * pawn_phase
    phase -= (len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK))) * knight_phase
    phase -= (len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.BLACK))) * bishop_phase
    phase -= (len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.BLACK))) * rook_phase
    phase -= (len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK))) * queen_phase

    phase = (phase * 256 + (total_phase / 2)) / total_phase

    return phase