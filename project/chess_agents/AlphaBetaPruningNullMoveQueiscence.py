import math
import os
import time

import chess
import chess.polyglot
import chess.gaviota
from project.chess_agents.agent import Agent
from project.chess_utilities.utility import Utility
from project.chess_utilities.NewUtility import NewUtility, board_value, eval_endgame, rate, get_num_pieces, MATE_SCORE
# Options
START_AS = "WHITE" # Human player plays as: WHITE, BLACK, or RANDOM
DEPTH = 5# Search depth, minimum 1
OPENING_BOOK = True # Use opening book?
ENDGAME_BOOK = False # Use endgame book?

# Constants
INF = float("inf")

# Other
ttable = {} # Transposition table
class AlphaBetaPruningNullMoveQueiscence(Agent):

    # Initialize your agent with whatever parameters you want
    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move)
        self.name = "The Best Agent"
        self.author = "Niels, Louis, Alexander"

    def calculate_move(self, board: chess.Board):
        """
        Chooses a move for the CPU
        If inside opening book make book move
        If inside Gaviota tablebase make tablebase move
        Else search for a move
        """
        self.flip_value = 1 if board.turn == chess.WHITE else -1

        global OPENING_BOOK

        if OPENING_BOOK:
            try:
                dir_path = os.path.dirname(os.path.realpath(__file__))
                with chess.polyglot.open_reader(
                        os.path.join(dir_path, "Opening_Book.bin")) as opening_book:  # https://sourceforge.net/projects/codekiddy-chess/files/
                    opening = opening_book.choice(board)
                    opening_book.close()
                    return opening.move
            except IndexError:
                OPENING_BOOK = False

        if ENDGAME_BOOK and get_num_pieces(board) <= 5:
            evals = []
            for move in list(board.legal_moves):
                board.push(move)
                score = eval_endgame(board)
                board.pop()
                evals.append((move, score))
            return max(evals, key=lambda eval: eval[1])[0]

        return self.iterative_deepening(board, DEPTH)[0]

    def iterative_deepening(self, board, depth):
        """
        Approaches the desired depth in steps for purposes of
        transposition and guesses for MTD(f), being overall
        more effective than searching at the desired depth immediately
        """
        time_start = time.time()
        max_search_time = 13
        for d in range(1, depth + 1):
            move, evaluation = self.negamax(board, d, -math.inf, math.inf)
            time_end = time.time()
            timer = time_end - time_start

            if (timer > max_search_time):
                break
        return (move, evaluation)

    def negamax(self, board, depth, alpha, beta):
        """
        Searches the possible moves using negamax, alpha-beta pruning, null-move pruning, and a transposition table
        Initial psuedocode adapated from Jeroen W.T. Carolus
        """
        alphaOrig = alpha
        #Return board position as zobrist hash
        key = chess.polyglot.zobrist_hash(board)

        # Search for position in the transposition table
        if key in ttable:
            tt_move, tt_score, tt_type, tt_depth = ttable[key]
            if tt_depth >= depth:
                if tt_type == "EXACT":
                    return (tt_move, tt_score)
                if tt_type == "LOWERBOUND" and tt_score > alpha:  # Update lowerbound alpha
                    alpha = tt_score
                elif tt_type == "UPPERBOUND" and tt_score < beta:  # Update upperbound beta
                    beta = tt_score

                if alpha >= beta:
                    return (tt_move, tt_score)

        if depth == 0 or board.is_game_over():
            score = self.flip_value*board_value(board)

            # Add position to the transposition table
            if abs(alpha - beta) > 1:  # Stops null window searches from being stored
                if score <= alpha:  # Score is lowerbound
                    ttable[key] = ("", score, "LOWERBOUND", depth)
                elif score >= beta:  # Score is upperbound
                    ttable[key] = ("", score, "UPPERBOUND", depth)
                else:  # Score is exact
                    ttable[key] = ("", score, "EXACT", depth)

            return ("", score)
        else:
            # Alpha-beta negamax
            score = 0
            best_move = ""
            best_score = -INF
            moves = list(board.legal_moves)
            moves.sort(key=lambda move: rate(board, move), reverse=True)

            for move in moves:
                board.push(move)
                score = -(self.negamax(board, depth - 1, -beta, -alpha)[1])
                board.pop()

                if score > best_score:
                    best_move = move
                    best_score = score

                alpha = max(alpha, best_score)

                if alpha >= beta:  # Beta cut-off
                    break

            # # Add position to the transposition table
            if abs(alpha - beta) > 1:  # Stops null window searches from being stored
                if best_score <= alphaOrig:  # Score is lowerbound
                    ttable[key] = (best_move, best_score, "LOWERBOUND", depth)
                elif best_score >= beta:  # Score is upperbound
                    ttable[key] = (best_move, best_score, "UPPERBOUND", depth)
                else:  # Score is exact
                    ttable[key] = (best_move, best_score, "EXACT", depth)

            return (best_move, best_score)
