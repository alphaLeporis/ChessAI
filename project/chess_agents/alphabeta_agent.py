from project.chess_agents.agent import Agent
import chess

from project.chess_utilities.board_score_utility import board_score_utility, board_value
from project.chess_utilities.utility import Utility
import time
import random

"""An example search agent with two implemented methods to determine the next move"""


class alphabeta_agent(Agent):

    # Initialize your agent with whatever parameters you want
    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move)
        self.name = "Alpha Beta search agent"
        self.author = "Louis, Alexander & Niels"

    # This agent does not perform any searching, it sinmply iterates trough all the moves possible and picks the one with the highest utility
    def calculate_move(self, board: chess.Board):

        start_time = time.time()

        # If the agent is playing as black, the utility values are flipped (negative-positive)
        flip_value = 1 if board.turn == chess.WHITE else -1

        best_move = minimax_root(3, board, True)
        print("Total time: "+str(time.time()-start_time))

        return best_move



def minimax(depth, board, alpha, beta, is_maximising_player):
    if (depth == 0):
        return board_value(board)
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

def minimax_root(depth, board, is_maximising_player=False):
    # only search the top 50% moves
    best_move = -9999
    best_move_found = None

    start_time = time.time()
    for move in board.legal_moves:
        if time.time() - start_time > 5:
            break
        board.push(move)
        value = minimax(depth - 1, board, -10000, 10000, not is_maximising_player)
        board.pop()
        if (value >= best_move):
            best_move = value
            best_move_found = move

    for move in board.legal_moves:
        if time.time() - start_time > 5:
            break
        board.push(move)
        value = minimax(depth, board, -10000, 10000, is_maximising_player)
        board.pop()
        if (value >= best_move):
            best_move = value
            best_move_found = move

    for move in board.legal_moves:
        if time.time() - start_time > 5:
            break
        board.push(move)
        value = minimax(depth+1, board, -10000, 10000, is_maximising_player)
        board.pop()
        if (value >= best_move):
            best_move = value
            best_move_found = move
    return best_move_found
