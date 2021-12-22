import chess
from project.chess_utilities.utility import Utility

mvv_storing = 10  # How many of the MVV_LVV top candidates to use
no_of_killer_moves = 2  # Number of killer moves stored per depth
R = 2  # Null move reduction of depth


# Piece base values
piece_value = {chess.KING: 60000,
                             chess.QUEEN: 900,
                             chess.ROOK: 490,
                             chess.BISHOP: 320,
                             chess.KNIGHT: 290,
                             chess.PAWN: 100}


king_mid = [0,   0,   0,   0,   0,   0,   0,   0,   0, 0,
            0,   0,   0,   0,   0,   0,   0,   0,   0, 0,
            0, -30, -40, -40, -50, -50, -40, -40, -30, 0,
            0, -30, -40, -40, -50, -50, -40, -40, -30, 0,
            0, -30, -40, -40, -50, -50, -40, -40, -30, 0,
            0, -30, -40, -40, -50, -50, -40, -40, -30, 0,
            0, -20, -30, -30, -40, -40, -30, -30, -20, 0,
            0, -10, -20, -20, -20, -20, -20, -20, -10, 0,
            0,  20,  20,   0,   0,   0,   0,  20,  20, 0,
            0,  0,  20,   40,   0,   0,   0,  40,  20, 0,
            0,   0,   0,   0,   0,   0,   0,   0,   0, 0,
            0,   0,   0,   0,   0,   0,   0,   0,   0, 0]
queen_mid = [0,   0,   0,   0,  0,  0,   0,   0,   0, 0,
             0,   0,   0,   0,  0,  0,   0,   0,   0, 0,
             0, -20, -10, -10, -5, -5, -10, -10, -20, 0,
             0, -10,   0,   0,  0,  0,   0,   0, -10, 0,
             0, -10,   0,   5,  5,  5,   5,   0, -10, 0,
             0,  -5,   0,   5,  5,  5,   5,   0,  -5, 0,
             0,  -5,   0,   5,  5,  5,   5,   0,  -5, 0,
             0, -10,   5,   5,  5,  5,   5,   0, -10, 0,
             0, -10,   0,   5,  0,  0,   0,   0, -10, 0,
             0, -20, -10, -10,  0,  0, -10, -10, -20, 0,
             0,   0,   0,   0,  0,  0,   0,   0,   0, 0,
             0,   0,   0,   0,  0,  0,   0,   0,   0, 0]
rook_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 5, 15, 15, 15, 15, 15, 15, 5, 0,
            0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
            0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
            0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
            0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
            0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
            0, 0, 0, 10, 10, 10, 10, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bishop_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, -20, -10, -10, -10, -10, -10, -10, -20, 0,
              0, -10, 0, 0, 0, 0, 0, 0, -10, 0,
              0, -10, 0, 5, 10, 10, 5, 0, -10, 0,
              0, -10, 5, 5, 10, 10, 5, 5, -10, 0,
              0, -10, 0, 10, 10, 10, 10, 0, -10, 0,
              0, -10, 10, 10, 10, 10, 10, 10, -10, 0,
              0, -10, 10, 0, 10, 10, 0, 10, -10, 0,
              0, -20, -10, -50, -10, -10, -50, -10, -20, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
knight_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, -30, -30, -10, -10, -10, -10, -30, -30, 0,
              0, -20, -20, 0, 0, 0, 0, -20, -20, 0,
              0, -10, 0, 10, 15, 15, 10, 0, -10, 0,
              0, -10, 5, 15, 20, 20, 15, 5, -10, 0,
              0, -10, 0, 15, 20, 20, 15, 0, -10, 0,
              0, -10, 5, 10, 15, 15, 10, 5, -10, 0,
              0, -20, -20, 0, 5, 5, 0, -20, -20, 0,
              0, -30, -30, -10, -10, -10, -10, -30, -30, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
pawn_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 50, 50, 50, 50, 50, 50, 50, 50, 0,
            0, 20, 20, 20, 30, 30, 20, 20, 20, 0,
            0, 10, 10, 10, 25, 25, 10, 10, 10, 0,
            0, 0, 0, 0, 20, 20, 0, 0, 0, 0,
            0, 5, -5, -10, 0, 0, -10, -5, 5, 0,
            0, 5, 10, 10, -20, -20, 10, 10, 5, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

king_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, -24, -23, -22, -21, -21, -22, -23, -24, 0,
            0, -23, -12, -10,  -10, -10, -10, -10, -23, 0,
            0, -22, -10,  20,  30, 30, 20, -10, -22, 0,
            0, -21, -10,  30,  40, 40, 30, -10, -21, 0,
            0, -21, -10,  30,  40, 40, 30, -10, -21, 0,
            0, -22, -10,  20,  30,  30,  20, -10, -22, 0,
            0, -23, -12, -10, -10, -10,  -10, -12, -23, 0,
            0, -24, -23, -22, -21, -21, -22, -23, -24, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
queen_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, -20, -10, -10, -5, -5, -10, -10, -20, 0,
             0, -10, 0, 0, 0, 0, 0, 0, -10, 0,
             0, -10, 0, 5, 5, 5, 5, 0, -10, 0,
             0, -5, 0, 5, 5, 5, 5, 0, -5, 0,
             0, -5, 0, 5, 5, 5, 5, 0, -5, 0,
             0, -10, 5, 5, 5, 5, 5, 0, -10, 0,
             0, -10, 0, 5, 0, 0, 0, 0, -10, 0,
             0, -20, -10, -10, 0, 0, -10, -10, -20, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
rook_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 5, 15, 15, 15, 15, 15, 15, 5, 0,
            0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
            0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
            0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
            0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
            0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
            0, 0, 0, 5, 10, 10, 5, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bishop_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, -20, -10, -10, -10, -10, -10, -10, -20, 0,
              0, -10, 0, 0, 0, 0, 0, 0, -10, 0,
              0, -10, 0, 5, 10, 10, 5, 0, -10, 0,
              0, -10, 5, 5, 10, 10, 5, 5, -10, 0,
              0, -10, 0, 10, 10, 10, 10, 0, -10, 0,
              0, -10, 10, 10, 10, 10, 10, 10, -10, 0,
              0, -10, 5, 0, 0, 0, 0, 5, -10, 0,
              0, -20, -10, -10, -10, -10, -10, -10, -20, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
knight_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, -50, -40, -30, -30, -30, -30, -40, -50, 0,
              0, -40, -20, 0, 0, 0, 0, -20, -40, 0,
              0, -30, 0, 10, 15, 15, 10, 0, -30, 0,
              0, -30, 5, 15, 20, 20, 15, 5, -30, 0,
              0, -30, 0, 15, 20, 20, 15, 0, -30, 0,
              0, -30, 5, 10, 15, 15, 10, 5, -30, 0,
              0, -40, -20, 0, 5, 5, 0, -20, -40, 0,
              0, -50, -40, -30, -30, -30, -30, -40, -50, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
pawn_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 50, 50, 50, 50, 50, 50, 50, 50, 0,
            0, 30, 30, 30, 30, 30, 30, 30, 30, 0,
            0, 20, 20, 20, 25, 25, 20, 20, 20, 0,
            0, 10, 10, 10, 10, 10, 10, 10, 10, 0,
            0, -5, -5, -5, -5, -5, -5, -5, -5, 0,
            0, -10, -10, -10, -20, -20, -10, -10, -10, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

piece_value_mid_game = {'K': king_mid,
                        'Q': queen_mid,
                        'R': rook_mid,
                        'B': bishop_mid,
                        'N': knight_mid,
                        'p': pawn_mid}

piece_value_end_game = {'K': king_end,
                        'Q': queen_end,
                        'R': rook_end,
                        'B': bishop_end,
                        'N': knight_end,
                        'p': pawn_end}

piece_phase_calc = {'K': 0,
                    'Q': 4,
                    'R': 2,
                    'B': 1,
                    'N': 1,
                    'p': 0}

endgame_phase_limit = 14  # Game phase starts at 24. When down to 14 or less then it is considered endgame. Tune this factor later

class NewerUtility(Utility):

    def __init__(self) -> None:
        pass

    # Calculate the amount of white pieces minus the amount of black pieces
    def board_value(self, board: chess.Board, move :chess.Move):
        for piece in board.pieces(piece_type=chess.PAWN, color=chess.WHITE):
            value = piece_value[piece] +



        if(board.is_checkmate()):
            return 1e9 if board.turn == chess.WHITE else -1e9
        if(board.is_stalemate()):
            return 0

        n_white, n_black = self.material_eval(board)

        if board.ply() < 30:
            if board.is_castling(board.peek()):
                if board.turn == chess.WHITE :
                    n_white += 50
                else:
                    n_black += 50

        #Bischop pair bonus
        if(len(board.pieces(piece_type=chess.BISHOP, color=chess.WHITE)) == 2):
            n_white += 15
        if (len(board.pieces(piece_type=chess.BISHOP, color=chess.BLACK)) == 2):
            n_black += 15

        return n_white - n_black

    def material_eval(self, board):
        """
        Evaluate material advantage by finding the difference in
        material between white and black
        Values from Tomasz Michniewski's Simplified Evaluation Function
        """
        pawn_value = 100
        knight_value = 350
        bishop_value = 350
        rook_value = 525
        queen_value = 1000
        king_value = 200000

        n_white = 0
        n_white += len(board.pieces(piece_type=chess.PAWN, color=chess.WHITE))*pawn_value
        n_white += len(board.pieces(piece_type=chess.BISHOP, color=chess.WHITE))*bishop_value
        n_white += len(board.pieces(piece_type=chess.KNIGHT, color=chess.WHITE))*knight_value
        n_white += len(board.pieces(piece_type=chess.ROOK, color=chess.WHITE))*rook_value
        n_white += len(board.pieces(piece_type=chess.QUEEN, color=chess.WHITE))*queen_value
        n_white += len(board.pieces(piece_type=chess.KING, color=chess.WHITE))*king_value


        n_black = 0
        n_black += len(board.pieces(piece_type=chess.PAWN, color=chess.BLACK))*pawn_value
        n_black += len(board.pieces(piece_type=chess.BISHOP, color=chess.BLACK))*bishop_value
        n_black += len(board.pieces(piece_type=chess.KNIGHT, color=chess.BLACK))*knight_value
        n_black += len(board.pieces(piece_type=chess.ROOK, color=chess.BLACK))*rook_value
        n_black += len(board.pieces(piece_type=chess.QUEEN, color=chess.BLACK))*queen_value
        n_black += len(board.pieces(piece_type=chess.KING, color=chess.BLACK))*king_value

        return (n_white, n_black)

    def evaluate_piece(piece: chess.Piece, square: chess.Square, end_game: bool) -> int:
        piece_type = piece.piece_type
        mapping = []
        if piece_type == chess.PAWN:
            mapping = pawnEvalWhite if piece.color == chess.WHITE else pawnEvalBlack
        if piece_type == chess.KNIGHT:
            mapping = knightEval
        if piece_type == chess.BISHOP:
            mapping = bishopEvalWhite if piece.color == chess.WHITE else bishopEvalBlack
        if piece_type == chess.ROOK:
            mapping = rookEvalWhite if piece.color == chess.WHITE else rookEvalBlack
        if piece_type == chess.QUEEN:
            mapping = queenEval
        if piece_type == chess.KING:
            # use end game piece-square tables if neither side has a queen
            if end_game:
                mapping = (
                    kingEvalEndGameWhite
                    if piece.color == chess.WHITE
                    else kingEvalEndGameBlack
                )
            else:
                mapping = kingEvalWhite if piece.color == chess.WHITE else kingEvalBlack

        return mapping[square]

    def evualuate_pice(self, pice: chess.Piece, square: chess.Square, end_game: bool) -> int:

