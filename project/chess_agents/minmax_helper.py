import time

import chess
import chess.svg
from collections import OrderedDict
from operator import itemgetter
import pandas as pd
import numpy as np
import tensorflow as tf

from project.chess_agents.ml_helper import find_best_moves

pawn_white_eval = np.array([[5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
                            [3.0, 3.0, 3.0, 4.0, 4.0, 3.0, 3.0, 3.0],
                            [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
                            [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
                            [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
                            [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
                            [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], np.float)

pawn_black_eval = pawn_white_eval[::-1]

knight_white_eval = np.array([[-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
                              [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
                              [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
                              [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
                              [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
                              [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
                              [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
                              [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]], np.float)

knight_black_eval = knight_white_eval[::-1]

bishop_white_eval = np.array([[-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
                              [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
                              [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
                              [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
                              [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
                              [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
                              [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
                              [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]], np.float)

bishop_black_eval = bishop_white_eval[::-1]

rook_white_eval = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
                            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
                            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
                            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
                            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
                            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
                            [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]], np.float)

rook_black_eval = rook_white_eval[::-1]

queen_white_eval = np.array([[2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
                             [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
                             [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
                             [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
                             [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
                             [-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
                             [-1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0],
                             [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]], np.float)

queen_black_eval = queen_white_eval[::-1]

king_white_eval = np.array([[-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                            [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
                            [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
                            [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
                            [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]], np.float)

king_black_eval = king_white_eval[::-1]


def square_to_coord(square):
    """Convert square to coordinates
    """
    return {0: (7, 0), 1: (7, 1), 2: (7, 2), 3: (7, 3), 4: (7, 4), 5: (7, 5), 6: (7, 6), 7: (7, 7),
            8: (6, 0), 9: (6, 1), 10: (6, 2), 11: (6, 3), 12: (6, 4), 13: (6, 5), 14: (6, 6), 15: (6, 7),
            16: (5, 0), 17: (5, 1), 18: (5, 2), 19: (5, 3), 20: (5, 4), 21: (5, 5), 22: (5, 6), 23: (5, 7),
            24: (4, 0), 25: (4, 1), 26: (4, 2), 27: (4, 3), 28: (4, 4), 29: (4, 5), 30: (4, 6), 31: (4, 7),
            32: (3, 0), 33: (3, 1), 34: (3, 2), 35: (3, 3), 36: (3, 4), 37: (3, 5), 38: (3, 6), 39: (3, 7),
            40: (2, 0), 41: (2, 1), 42: (2, 2), 43: (2, 3), 44: (2, 4), 45: (2, 5), 46: (2, 6), 47: (2, 7),
            48: (1, 0), 49: (1, 1), 50: (1, 2), 51: (1, 3), 52: (1, 4), 53: (1, 5), 54: (1, 6), 55: (1, 7),
            56: (0, 0), 57: (0, 1), 58: (0, 2), 59: (0, 3), 60: (0, 4), 61: (0, 5), 62: (0, 6), 63: (0, 7)}[square]


def get_piece_value(board, piece, square):
    """Return the value of a piece
    """
    x, y = square_to_coord(square)

    if (board.turn == chess.WHITE):
        sign_white = -1
        sign_black = 1
    else:
        sign_white = 1
        sign_black = -1

    if (piece == 'None'):
        return 0
    elif (piece == 'P'):
        return sign_white * (10 + pawn_white_eval[x][y])
    elif (piece == 'N'):
        return sign_white * (30 + knight_white_eval[x][y])
    elif (piece == 'B'):
        return sign_white * (30 + bishop_white_eval[x][y])
    elif (piece == 'R'):
        return sign_white * (50 + rook_white_eval[x][y])
    elif (piece == 'Q'):
        return sign_white * (90 + queen_white_eval[x][y])
    elif (piece == 'K'):
        return sign_white * (900 + king_white_eval[x][y])
    elif (piece == 'p'):
        return sign_black * (10 + pawn_black_eval[x][y])
    elif (piece == 'n'):
        return sign_black * (30 + knight_black_eval[x][y])
    elif (piece == 'b'):
        return sign_black * (30 + bishop_black_eval[x][y])
    elif (piece == 'r'):
        return sign_black * (50 + rook_black_eval[x][y])
    elif (piece == 'q'):
        return sign_black * (90 + queen_black_eval[x][y])
    elif (piece == 'k'):
        return sign_black * (900 + king_black_eval[x][y])


def evaluate_board(board):
    """Return the evaluation of a board
    """
    evaluation = 0
    for square in chess.SQUARES:
        piece = str(board.piece_at(square))
        evaluation = evaluation + get_piece_value(board, piece, square)
    return evaluation


def minimax(depth, board, alpha, beta, is_maximising_player):
    if (depth == 0):
        return - evaluate_board(board)
    elif (depth > 3):
        legal_moves = find_best_moves(board, model, 0.75)
    else:
        legal_moves = list(board.legal_moves)

    if (is_maximising_player):
        best_move = -9999
        for move in legal_moves:
            board.push(move)
            best_move = max(best_move, minimax(depth - 1, board, alpha, beta, not is_maximising_player))
            board.pop()
            alpha = max(alpha, best_move)
            if (beta <= alpha):
                return best_move
        return best_move
    else:
        best_move = 9999
        for move in legal_moves:
            board.push(move)
            best_move = min(best_move, minimax(depth - 1, board, alpha, beta, not is_maximising_player))
            board.pop()
            beta = min(beta, best_move)
            if (beta <= alpha):
                return best_move
        return best_move

path_to_model = '../../chess-engine-model/latest-model'

global model
model = tf.saved_model.load(path_to_model)

def minimax_root(depth, board, is_maximising_player=True):
    # only search the top 50% moves
    legal_moves = find_best_moves(board, model)
    best_move = -9999
    best_move_found = None

    for move in legal_moves:
        board.push(move)
        value = minimax(depth - 1, board, -10000, 10000, not is_maximising_player)
        board.pop()
        if (value >= best_move):
            best_move = value
            best_move_found = move
    if not legal_moves:
        best_move_found = list(board.legal_moves)[0]
    return best_move_found