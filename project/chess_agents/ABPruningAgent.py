import time

from project.chess_agents.agent import Agent
import math
import chess

from project.chess_utilities.utility import Utility

INF = math.inf

class ABPruningAgent(Agent):

    # Initialize your agent with whatever parameters you want
    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move)
        self.name = "Alpha Beta search"
        self.author = "Alexander, Louis & Niels"
        print("Init")

    def calculate_move(self, board):
        start_time = time.time()
        self.flip_value = 1 if board.turn == chess.WHITE else -1

        # minimax search with alpha-beta cut
        best_score = -INF
        beta = INF
        best_action = None
        currentDepth = 1
        maxDepth = 10

        timeSpend = 0
        while currentDepth <= maxDepth:
            # Zien dat we niet nog eens een diepte beginnen zodat we over de tijd gaan
            # Het houd rekening met de tijd die ervoor is over gadaan * een factor om de extra diepte te kunne inschatten
            if time.time() - start_time + timeSpend*1.3 > self.time_limit_move:
                return best_action
            else:
                timeSpend = time.time()
                for move in list(board.legal_moves):
                    board.push(move)
                    v = self.min_value(board, best_score, beta, currentDepth - 1)
                    board.pop()
                    if v > best_score:
                        best_score = v
                        best_action = move
                    timeSpend = time.time() - timeSpend
            print("The current depth is -> " + str(currentDepth))
            currentDepth+= 1


    def max_value(self, board, alpha, beta, depth):
        if depth <= 0:
            # print(self.flip_value*self.utility.board_value(board))
            return self.flip_value*self.utility.board_value(board)
        v = -INF
        for move in list(board.legal_moves):
            board.push(move)
            v = max(v, self.min_value(board, alpha, beta, depth - 1))
            board.pop()
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, board, alpha, beta, depth):
        if depth <= 0:
            # print(self.flip_value*self.utility.board_value(board))
            return self.flip_value*self.utility.board_value(board)
        v = INF
        for move in list(board.legal_moves):
            board.push(move)
            v = min(v, self.max_value(board, alpha, beta, depth - 1))
            board.pop()
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v