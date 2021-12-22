import random
from project.chess_agents.agent import Agent
import math
import chess

from project.chess_utilities.utility import Utility


class ABPruningAgent(Agent):

    # Initialize your agent with whatever parameters you want
    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move)
        self.name = "ABPruningAGent"
        self.author = "Niels, Louis, Alexander"

    def calculate_move(self, board):
        self.flip_value = 1 if board.turn == chess.WHITE else -1

        # minimax search with alpha-beta cut
        depth = 5
        INF = float('inf')
        best_score = -INF
        beta = INF
        best_action = None
        for move in list(board.legal_moves):
            board.push(move)
            v = self.min_value(board, best_score, beta, depth - 1)
            board.pop()
            if v > best_score:
                best_score = v
                best_action = move
        return best_action

    def max_value(self, board, alpha, beta, depth):
        if depth <= 0:
            print(self.flip_value*self.utility.board_value(board))
            return self.flip_value*self.utility.board_value(board)
        INF = float('inf')
        v = -INF
        movelist = list(board.legal_moves)
        random.shuffle(movelist) #shuffle successor states in order to improve performance
        for move in movelist:
            board.push(move)
            v = max(v, self.min_value(board, alpha, beta, depth - 1))
            board.pop()
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, board, alpha, beta, depth):
        if depth <= 0:
            print(self.flip_value*self.utility.board_value(board))
            return self.flip_value*self.utility.board_value(board)
        INF = float('inf')
        v = INF
        movelist = list(board.legal_moves)
        random.shuffle(movelist) #shuffle successor states in order to improve performance
        for move in movelist:
            board.push(move)
            v = min(v, self.max_value(board, alpha, beta, depth - 1))
            board.pop()
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v