import random
from project.chess_agents.agent import Agent
import math
import chess

from project.chess_utilities.utility import Utility


class QuiescenceAgent(Agent):

    # Initialize your agent with whatever parameters you want
    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move)
        self.name = "ABPruningAGent"
        self.author = "Niels, Louis, Alexander"

    def quiescence_Search(self, board, max_depth, current_depth, is_max_player, alpha, beta, nodes_per_depth):
        # This if else code block is only used for analysis of algorithm, by counting number of nodes explored
        self.flip_value = 1 if board.turn == chess.WHITE else -1

        if current_depth == 0:
            leaf_node_score = self.flip_value * self.utility.board_value(board)
            return (leaf_node_score, nodes_per_depth)

        if max_depth - current_depth > 3:
            all_possible_capture_moves = [move for move in board.legal_moves if
                                          self.utility.is_favorable_move(board, move)]
        else:
            all_possible_capture_moves = board.legal_moves

        if is_max_player:

            # set absurdly high negative value such that none of the static evaluation result less than this value
            best_score = -100000

            for legal_move in all_possible_capture_moves:
                move = chess.Move.from_uci(str(legal_move))

                # pusshing the current move to the board
                board.push(move)

                # calculating node score, if the current node will be the leaf node, then score will be calculated by static evaluation;
                # score will be calculated by finding max value between node score and current best score.
                node_score, nodes_per_depth = self.quiescence_Search(board, max_depth, current_depth - 1, False, alpha,
                                                                     beta, nodes_per_depth)

                # calculating best score by finding max value between current best score and node score
                best_score = max(best_score, node_score)

                # undoing the last move, so as to explore new moves while backtracking
                board.pop()

                # calculating alpha for current MAX node
                alpha = max(alpha, best_score)

                # beta cut off
                if beta <= alpha:
                    return (best_score)

            return (best_score, nodes_per_depth)
        else:

            # set absurdly high positive value such that none of the static evaluation result more than this value
            best_score = 100000

            for legal_move in all_possible_capture_moves:
                move = chess.Move.from_uci(str(legal_move))

                # pushing the current move to the board
                board.push(move)

                # calculating node score, if the current node will be the leaf node, then score will be calculated by static evaluation;
                # score will be calculated by finding min value between node score and current best score.
                node_score, nodes_per_depth = self.quiescence_Search(board, max_depth, current_depth - 1, True, alpha,
                                                                     beta, nodes_per_depth)

                # calculating best score by finding min value between current best score and node score
                best_score = min(best_score, node_score)

                # undoing the last move, so as to explore new moves while backtracking
                board.pop()

                # calculating alpha for current MIN node
                beta = min(beta, best_score)

                # beta cut off
                if beta <= alpha:
                    return (best_score)

            return (best_score)

    def calculate_move(self, board):
        depth = 5
        is_max_player = True if board.turn == chess.WHITE else False
        alpha = -10000
        beta = 10000
        best_move_score = -1000000
        best_move = None
        for legal_move in board.legal_moves:
            move = chess.Move.from_uci(str(legal_move))
            board.push(move)
            move_score, nodes_per_depth = self.quiescence_Search(board, depth, depth, is_max_player, alpha, beta, {})
            score = max(best_move_score, move_score)
            board.pop()
            if score > best_move_score:
                best_move_score = score
                best_move = move
        return (best_move)
