from project.chess_agents.agent import Agent
import chess
import chess.svg
from collections import OrderedDict
from operator import itemgetter
import pandas as pd
import numpy as np
import tensorflow as tf

from project.chess_agents.choose_opening import choose_opening
from project.chess_agents.minmax_helper import minimax_root
from project.chess_agents.ml_helper import get_possible_moves_data, predict, can_checkmate
from project.chess_utilities.utility import Utility
import time
import random

"""An example search agent with two implemented methods to determine the next move"""


class MLAgent(Agent):

    # Initialize your agent with whatever parameters you want
    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move)
        self.name = "Super Duper ML agent"
        self.author = "Louis"

    # This agent does not perform any searching, it sinmply iterates trough all the moves possible and picks the one with the highest utility
    def calculate_move(self, board: chess.Board):
        start_time = time.time()
        for move in board.legal_moves:
            if (can_checkmate(move, board)):
                print("Total time: " + str(time.time() - start_time) + "s")
                return move

        nb_moves = len(list(board.legal_moves))

        if (nb_moves > 30):
            usedMove = minimax_root(3, board)
        elif (nb_moves > 10 and nb_moves <= 30):
            usedMove = minimax_root(4, board)
        else:
            usedMove = minimax_root(5, board)

        print("Total time: " + str(time.time() - start_time) + "s")
        return usedMove
