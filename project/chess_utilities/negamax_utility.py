import chess
from project.chess_utilities.utility import Utility

# piece square tables
bPawnTable = [0,  0,  0,  0,  0,  0,  0,  0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                 5,  5, 10, 25, 25, 10,  5,  5,
                 0,  0,  0, 20, 20,  0,  0,  0,
                 5, -5,-10,  0,  0,-10, -5,  5,
                 5, 10, 10,-20,-20, 10, 10,  5,
                 0,  0,  0,  0,  0,  0,  0,  0]
wPawnTable = bPawnTable[::-1]
bKnightTable = [-50,-40,-30,-30,-30,-30,-40,-50,
                -40,-20,  0,  0,  0,  0,-20,-40,
                -30,  0, 10, 15, 15, 10,  0,-30,
                -30,  5, 15, 20, 20, 15,  5,-30,
                -30,  0, 15, 20, 20, 15,  0,-30,
                -30,  5, 10, 15, 15, 10,  5,-30,
                -40,-20,  0,  5,  5,  0,-20,-40,
                -50,-40,-30,-30,-30,-30,-40,-50]
wKnightTable = bKnightTable[::-1]
bBishopTable = [-20,-10,-10,-10,-10,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5, 10, 10,  5,  0,-10,
                -10,  5,  5, 10, 10,  5,  5,-10,
                -10,  0, 10, 10, 10, 10,  0,-10,
                -10, 10, 10, 10, 10, 10, 10,-10,
                -10,  5,  0,  0,  0,  0,  5,-10,
                -20,-10,-10,-10,-10,-10,-10,-20]
wBishopTable = bBishopTable[::-1]
bRookTable = [0,  0,  0,  0,  0,  0,  0,  0,
                  5, 10, 10, 10, 10, 10, 10,  5,
                 -5,  0,  0,  0,  0,  0,  0, -5,
                 -5,  0,  0,  0,  0,  0,  0, -5,
                 -5,  0,  0,  0,  0,  0,  0, -5,
                 -5,  0,  0,  0,  0,  0,  0, -5,
                 -5,  0,  0,  0,  0,  0,  0, -5,
                  0,  0,  0,  5,  5,  0,  0,  0]
wRookTable = bRookTable[::-1]
bQueenTable = [-20,-10,-10, -5, -5,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5,  5,  5,  5,  0,-10,
                 -5,  0,  5,  5,  5,  5,  0, -5,
                  0,  0,  5,  5,  5,  5,  0, -5,
                -10,  5,  5,  5,  5,  5,  0,-10,
                -10,  0,  5,  0,  0,  0,  0,-10,
                -20,-10,-10, -5, -5,-10,-10,-20]
wQueenTable = bQueenTable[::-1]


class NegaMaxUtility(Utility):

    def __init__(self) -> None:
        pass

    # Calculate the amount of white pieces minus the amount of black pieces
    def board_value(self, board: chess.Board):
        evaluation = 5  # setting bias to 5 to try and avoid draws
        pieces = board.pieces
        # Get all pieces
        white_pawns = pieces(1, True)
        black_pawns = pieces(1, False)
        white_knights = pieces(2, True)
        black_knights = pieces(2, False)
        white_bishops = pieces(3, True)
        black_bishops = pieces(3, False)
        white_rooks = pieces(4, True)
        black_rooks = pieces(4, False)
        white_queens = pieces(5, True)
        black_queens = pieces(5, False)
        # Calculate Material Advantage (centipawns)
        # mapping pieces to piece-square tables
        evaluation += sum(map(lambda x: wPawnTable[x], white_pawns)) - sum(map(lambda x: bPawnTable[x], black_pawns))
        evaluation += sum(map(lambda x: wKnightTable[x], white_knights)) - sum(
            map(lambda x: bKnightTable[x], black_knights))
        evaluation += sum(map(lambda x: wBishopTable[x], white_bishops)) - sum(
            map(lambda x: bBishopTable[x], black_bishops))
        evaluation += sum(map(lambda x: wRookTable[x], white_rooks)) - sum(map(lambda x: bRookTable[x], black_rooks))
        evaluation += sum(map(lambda x: wQueenTable[x], white_queens)) - sum(
            map(lambda x: bQueenTable[x], black_queens))
        # calculating material advantage
        evaluation += 100 * (len(white_pawns) - len(black_pawns)) + 310 * (
                    len(white_knights) - len(black_knights)) + 320 * (len(white_bishops) - len(black_bishops)) + 500 * (
                                  len(white_rooks) - len(black_rooks)) + 900 * (len(white_queens) - len(black_queens))
        return evaluation


