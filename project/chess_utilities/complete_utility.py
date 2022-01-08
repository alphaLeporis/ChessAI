import chess
from project.chess_utilities.utility import Utility
import project.chess_helpers.parameters as pa
import project.chess_helpers.board_phase as bp

class CompleteUtility(Utility):

    def __init__(self) -> None:
        pass

    # Calculate the amount of white pieces minus the amount of black pieces
    def board_value(self, board: chess.Board):
        if board.is_checkmate():
            return -pa.MATE_SCORE

        if board.is_fivefold_repetition() or board.is_stalemate():
            return 0

        # if ENDGAME_BOOK and get_num_pieces(board) <= 5:
        #    return eval_endgame(board)

        material_weight = 10
        psqt_weight = 10
        mobility_weight = 3

        material_score = self.material_eval(board)
        psqt_score = self.psqt_eval(board)
        mobility_score = self.mobility_eval(board)

        score = (material_score * material_weight) + (psqt_score * psqt_weight) + (mobility_score * mobility_weight)
        #score = (material_score * material_weight) + psqt_score

        score = round(score / 1000, 4)

        score += 0.4 * self.king_safety(board) if self.get_num_pieces(board) < 6 else 0
        score += 0.1 if len(board.pieces(chess.BISHOP, board.turn)) == 2 else 0
        score += 0.1 if len(board.pieces(chess.KNIGHT, board.turn)) == 2 else 0

        return score

    def material_eval(self, board):
        """
        Evaluate material advantage by finding the difference in
        material between white and black
        Values from Tomasz Michniewski's Simplified Evaluation Function
        """
        pawn_value = 100
        knight_value = 320
        bishop_value = 330
        rook_value = 500
        queen_value = 900
        king_value = pa.MATE_SCORE

        material_score = 0
        material_score += (len(board.pieces(chess.PAWN, board.turn)) - len(
            board.pieces(chess.PAWN, not board.turn))) * pawn_value
        material_score += (len(board.pieces(chess.KNIGHT, board.turn)) - len(
            board.pieces(chess.KNIGHT, not board.turn))) * knight_value
        material_score += (len(board.pieces(chess.BISHOP, board.turn)) - len(
            board.pieces(chess.BISHOP, not board.turn))) * bishop_value
        material_score += (len(board.pieces(chess.ROOK, board.turn)) - len(
            board.pieces(chess.ROOK, not board.turn))) * rook_value
        material_score += (len(board.pieces(chess.QUEEN, board.turn)) - len(
            board.pieces(chess.QUEEN, not board.turn))) * queen_value
        material_score += (len(board.pieces(chess.KING, board.turn)) - len(
            board.pieces(chess.KING, not board.turn))) * king_value

        return material_score


    def psqt_eval(self, board):
        """
        Piece-squares tables with tapered evaluation
        Values from Ronald Friederich's Rofchade engine
        Tapered evaluation from Fruit engine
        """
        phase = bp.get_phase(board)
        psqt_score = 0
        pieces_dict = board.piece_map()
        for pos in pieces_dict:
            piece = pieces_dict[pos]
            if piece.color == board.turn:
                value = 1
            else:
                value = -1
            mg_table = pa.mg_tables[piece.symbol()]
            eg_table = pa.eg_tables[piece.symbol()]
            psqt_mg_score = mg_table[7 - int(pos / 8)][pos % 8]
            psqt_eg_score = eg_table[7 - int(pos / 8)][pos % 8]
            psqt_score += (((psqt_mg_score * (256 - phase)) + (psqt_eg_score * phase)) / 256) * value
            psqt_score += pa.piece_val[piece.symbol()]*10 if board.turn else pa.piece_val[piece.symbol()]*-10

        return psqt_score


    def mobility_eval(self, board):
        """
        Evaluate mobility by getting the difference between the number of
        legal moves white has minus the number of legal moves black has
        """
        moves = list(board.legal_moves)
        mobility_score = 0
        for move in moves:
            if board.piece_at(move.from_square).color == board.turn:
                mobility_score += 1
            else:
                mobility_score -= 1

        return mobility_score

    def get_num_pieces(self, board):
        """
        Get the number of pieces of all types and color on the board.
        """
        num = 0
        for color in chess.COLORS:
            for piece in chess.PIECE_TYPES:
                num += (len(board.pieces(piece, color)))
        return num

    def king_safety(self,board):
        safety = 0
        King = board.king(board.turn)
        king = board.king(not board.turn)
        next_K = self.next_to_king(King)
        next_k = self.next_to_king(king)
        for square in next_K:
            safety = safety - len(list(board.attackers(not board.turn, square)))
        for square in next_k:
            safety = safety + len(list(board.attackers(board.turn, square)))
        return safety

    def next_to_king(self, king):
        vector = [-11, -10, -9, -1, 0, 1, 9, 10, 11]
        next_to = []
        for dep in vector:
            if pa.mailbox[pa.mailbox64[king] - dep] != -1:
                next_to.append(pa.mailbox64.index(pa.mailbox64[king] - dep))
        return next_to