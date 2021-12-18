import time

import chess
import chess.svg
from collections import OrderedDict
from operator import itemgetter
import pandas as pd
import numpy as np
import tensorflow as tf

path_to_model = '../../chess-engine-model/latest-model'

global model
model = tf.saved_model.load(path_to_model)

def predict(df_eval, imported_model):
    """Return array of predictions for each row of df_eval

    Keyword arguments:
    df_eval -- pd.DataFrame
    imported_model -- tf.saved_model
    """
    start_time = time.time()
    col_names = df_eval.columns
    dtypes = df_eval.dtypes
    predictions = []
    for row in df_eval.iterrows():
        example = tf.train.Example()
        for i in range(len(col_names)):
            dtype = dtypes[i]
            col_name = col_names[i]
            value = row[1][col_name]
            if dtype == 'object':
                value = bytes(value, 'utf-8')
                example.features.feature[col_name].bytes_list.value.extend([value])
            elif dtype == 'float':
                example.features.feature[col_name].float_list.value.extend([value])
            elif dtype == 'int':
                example.features.feature[col_name].int64_list.value.extend([value])
        predictions.append(imported_model.signatures['predict'](examples=tf.constant([example.SerializeToString()])))
    print("predict():"+ str(time.time() - start_time) + "s")
    return predictions


def get_board_features(board):
    """Return array of features for a board

    Keyword arguments:
    board -- chess.Board()
    """
    board_features = []
    for square in chess.SQUARES:
        board_features.append(str(board.piece_at(square)))
    return board_features


def get_move_features(move):
    """Return 2 arrays of features for a move

    Keyword arguments:
    move -- chess.Move
    """
    from_ = np.zeros(64)
    to_ = np.zeros(64)
    from_[move.from_square] = 1
    to_[move.to_square] = 1
    return from_, to_


def get_possible_moves_data(current_board):
    """Return pd.DataFrame of all possible moves used for predictions

    Keyword arguments:
    current_board -- chess.Board()
    """
    data = []
    moves = list(current_board.legal_moves)
    for move in moves:
        from_square, to_square = get_move_features(move)
        row = np.concatenate((get_board_features(current_board), from_square, to_square))
        data.append(row)

    board_feature_names = chess.SQUARE_NAMES
    move_from_feature_names = ['from_' + square for square in chess.SQUARE_NAMES]
    move_to_feature_names = ['to_' + square for square in chess.SQUARE_NAMES]

    columns = board_feature_names + move_from_feature_names + move_to_feature_names

    df = pd.DataFrame(data=data, columns=columns)

    for column in move_from_feature_names:
        df[column] = df[column].astype(float)
    for column in move_to_feature_names:
        df[column] = df[column].astype(float)
    return df


def find_best_moves(current_board, model, proportion=0.5):
    """Return array of the best chess.Move

    Keyword arguments:
    current_board -- chess.Board()
    model -- tf.saved_model
    proportion -- proportion of best moves returned
    """
    moves = list(current_board.legal_moves)
    df_eval = get_possible_moves_data(current_board)
    predictions = predict(df_eval, model)
    good_move_probas = []

    for prediction in predictions:
        proto_tensor = tf.make_tensor_proto(prediction['probabilities'])
        proba = tf.make_ndarray(proto_tensor)[0][1]
        good_move_probas.append(proba)

    dict_ = dict(zip(moves, good_move_probas))
    dict_ = OrderedDict(sorted(dict_.items(), key=itemgetter(1), reverse=True))

    best_moves = list(dict_.keys())

    return best_moves[0:int(len(best_moves) * proportion)]


def can_checkmate(move, current_board):
    """Return True if a move can checkmate

    Keyword arguments:
    move -- chess.Move
    current_board -- chess.Board()
    """
    fen = current_board.fen()
    future_board = chess.Board(fen)
    future_board.push(move)
    return future_board.is_checkmate()