import random
from project.chess_agents.agent import Agent
import math
import chess
INF = math.inf

class ABPruningAgent(Agent):
    def calculate_move(self, board):
        self.flip_value = 1 if board.turn == chess.WHITE else -1

        # minimax search with alpha-beta cut
        depth = 5
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
            #print(self.flip_value*self.utility.board_value(board))
            return self.flip_value*self.utility.board_value(board)
        v = -INF
        movelist = list(board.legal_moves)
        random.shuffle(movelist)
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
            #print(self.flip_value*self.utility.board_value(board))
            return self.flip_value*self.utility.board_value(board)
        v = INF
        movelist = list(board.legal_moves)
        random.shuffle(movelist)
        for move in movelist:
            board.push(move)
            v = min(v, self.max_value(board, alpha, beta, depth - 1))
            board.pop()
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v