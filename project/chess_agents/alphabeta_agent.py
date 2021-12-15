from project.chess_agents.agent import Agent
import chess
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

        best_move = random.sample(list(board.legal_moves), 1)[0]
        best_utility = 0
        # Loop trough all legal moves
        for move in list(board.legal_moves):
            # Check if the maximum calculation time for this move has been reached
            if time.time() - start_time > self.time_limit_move:
                break

        return best_move
