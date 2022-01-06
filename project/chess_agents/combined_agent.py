#  --------------------------------------------------------------------------------
#                                AI Brain
#  --------------------------------------------------------------------------------
import chess as chess
import chess.polyglot
import project.chess_helpers.combined_opening_move as om
import project.chess_helpers.combined_syzygy as sy

import time
import math

from project.chess_agents.agent import Agent
from project.chess_utilities.utility import Utility


class CombinedAgent(Agent):

    def __init__(self, utility: Utility, time_limit_move: float):
        super().__init__(utility, time_limit_move)
        # Transposition table init
        self.tt_entry = {'value': 0, 'flag': '', 'depth': 0, 'best move': None}
        self.tt_entry_q = {'value': 0, 'flag': ''}

        self.valid_moves_history = {}
        self.killer_moves = {}

        # Opening related parameters
        self.is_in_opening = True

        # Count the nodes searched, only for development purposes.
        self.counter = -1

        # Best moves from previous iterations
        self.best_moves = []

        # Used in the iterative deepening loop to stop after a certain time has passed
        self.timer = 0

        # To what depth it searched
        self.max_depth = 0
        self.real_depth = 0
        self.min_search_depth = 1
        self.max_search_depth = 8

    def calculate_move(self, board: chess.Board):

        # Init variables
        nodes = {}
        self.valid_moves_history = {}

        for depth in range(self.max_search_depth + 1):
            self.killer_moves[depth] = []

        start_color = 1 if board.turn == chess.WHITE else -1



        # Check if there is any opening moves to make in the current position
        if self.is_in_opening:
            time_start = time.time()
            move = om.make_opening_move(board)
            self.timer = time.time() - time_start
            evaluation = 0
            if not move:
                self.is_in_opening = False

        # Negamax with iterative deepening if not in opening
        if not self.is_in_opening:

            # Try if position is in syzygy tablebase, only in endgames
            # Only the 3, 4 and 5 piece tablebases are currently implemented
            if sum(board.piece_map())  <= 5:
                endgame_move, evaluation, dtz = sy.find_endgame_move(board)
                if endgame_move:

                    start_time = time.time()
                    # Also first try if can find an easy mate, if so play that
                    if abs(dtz) <= 1:
                        mate_depth = self.max_search_depth if self.max_search_depth < 6 else 6
                        endgame_move_2, evaluation_2 = self.negamax(board, mate_depth, -math.inf, math.inf, start_color, False)
                        self.timer = time.time() - start_time
                        if abs(evaluation_2) >= 1e6:
                            return endgame_move_2, evaluation_2

                    return endgame_move

            # Init parameters for iterative deepening
            self.tt_entry = {'value': 0, 'flag': '', 'depth': 0, 'best move': None, 'valid moves': []}
            self.best_moves = []

            # Iterative deepening
            start_time = time.time()
            for depth in range(1, self.max_search_depth + 1):

                move, evaluation = self.negamax(board, depth, -math.inf, math.inf, start_color, self.time_limit_move-(time.time()-start_time))
                self.best_moves.append([move, evaluation])

                nodes[depth] = self.counter - sum(nodes.values())
                print('Depth: ', depth)
                #  print('Nodes searched: ', nodes[depth])
                print('Time spent: ', round(time.time()-start_time, 2), 's\n')

                self.counter = -1

                # Break if time has run out, if reached at least min depth, or if finding a mate in lowest number of moves
                if (time.time()-start_time > self.time_limit_move and depth >= self.min_search_depth) or (evaluation / 100) > 100:
                    break
            print('----------------------------------')

            # Always return moves from an even number of depth, helps in some situation since quiescence search is not implemented
            self.max_depth = depth
            self.real_depth = self.max_depth
            if self.max_depth >= 2:
                evaluation = (self.best_moves[-1][1] + self.best_moves[-2][1]) / 2
                if len(self.best_moves) % 2 == 0:
                    move = self.best_moves[-1][0]
                else:
                    move = self.best_moves[-2][0]
                    self.max_depth -= 1

        return move

#  --------------------------------------------------------------------------------
#                            Negamax function
#  --------------------------------------------------------------------------------

    def negamax(self, board: chess.Board, depth, alpha, beta, color, max_time):
        global best_move
        alpha_original = alpha
        start_time = time.time()

        #  self.counter += 1

        # Transposition table lookup (https://en.wikipedia.org/wiki/Negamax#Negamax_with_alpha_beta_pruning_and_transposition_tables)
        key = chess.polyglot.zobrist_hash(board)
        if key in self.tt_entry and self.tt_entry[key]['depth'] >= depth:
            if self.tt_entry[key]['flag'] == 'exact':
                return self.tt_entry[key]['best move'], self.tt_entry[key]['value']
            elif self.tt_entry[key]['flag'] == 'lowerbound':
                alpha = max(alpha, self.tt_entry[key]['value'])
            elif self.tt_entry[key]['flag'] == 'upperbound':
                beta = min(beta, self.tt_entry[key]['value'])
            if alpha >= beta:
                return self.tt_entry[key]['best move'], self.tt_entry[key]['value']

        # Depth with quiescence search
        '''if depth == 0:
            if gamestate.piece_captured != '--':
                return None, self.quiescence(gamestate, -beta, -alpha, -color, 0)
            else:
                return None, e.evaluate(gamestate, depth) * color'''
        # Depth = 0 without quiescence search
        if depth == 0:
            return None, self.utility.board_value(board) * color

        # Don't search valid moves again if it has been done in last iteration
        if key in self.valid_moves_history and self.valid_moves_history[key]:
            children = self.valid_moves_history[key]
        else:
            children = board.legal_moves
            self.valid_moves_history[key] = children

        # Check if there is a checkmate or stalemate
        if board.is_checkmate() or board.is_stalemate():
            return None, self.utility.board_value(board) * color


        # Sort moves before Negamax
        children = self.sort_moves(board, list(children), depth)

        # Negamax loop
        max_eval = -math.inf
        for child in reversed(children):
            if (time.time() - start_time > max_time):
                break

            board.push(child)

            score = -self.negamax(board, depth - 1, -beta, -alpha, -color, max_time-(time.time()-start_time))[1]
            board.pop()

            if score > max_eval:
                max_eval = score
                best_move = child
            alpha = max(alpha, max_eval)

            # Beta cutoff
            if beta <= alpha:

                # Killer moves
                if board.is_capture(child):
                    self.killer_moves[depth].append(child)
                    if len(self.killer_moves[depth]) == 2:  # Keep killer moves at a maximum of x per depth
                        self.killer_moves[depth].pop(0)
                break

        # Transposition table saving
        key = chess.polyglot.zobrist_hash(board)
        self.tt_entry[key] = {'value': max_eval}
        if max_eval <= alpha_original:
            self.tt_entry[key]['flag'] = 'upperbound'
        elif max_eval >= beta:
            self.tt_entry[key]['flag'] = 'lowerbound'
        else:
            self.tt_entry[key]['flag'] = 'exact'

        self.tt_entry[key]['depth'] = depth
        self.tt_entry[key]['best move'] = best_move

        return best_move, max_eval

#  --------------------------------------------------------------------------------
#                           Quiescence search
#  --------------------------------------------------------------------------------
    piece_values = {
        chess.BISHOP: 330,
        chess.KING: 20_000,
        chess.KNIGHT: 320,
        chess.PAWN: 100,
        chess.QUEEN: 900,
        chess.ROOK: 500,
    }

    def quiescence(self, board, alpha, beta, color, moves):

        moves += 1

        # Check if value is in table
        key = chess.polyglot.zobrist_hash(board)
        if key in self.tt_entry_q:
            if self.tt_entry_q[key]['flag'] == 'exact':
                score = self.tt_entry_q[key]['value']
            else:
                score = color * self.utility.board_value(board)
                self.tt_entry_q[key] = {'flag': 'exact'}
                self.tt_entry_q[key]['value'] = score
        else:
            score = self.utility.board_value(board)
            self.tt_entry_q[key] = {'flag': 'exact'}
            self.tt_entry_q[key]['value'] = score

        big_delta = 200
        if score < alpha - big_delta:
            return alpha
        if score >= beta:
            return beta
        if alpha < score:
            alpha = score

        # If having looked through 2 moves then stop and return value
        if moves >= 3:
            return score

        # Don't search valid moves again if it has been done in last iteration
        if key in self.valid_moves_history and self.valid_moves_history[key]:
            children = self.valid_moves_history[key]
        else:
            children = board.legal_moves
            self.valid_moves_history[key] = children

        children = self.sort_moves(board, list(children), 0)

        for child in children:

            # Only look at capture moves (and later checks)
            if board.is_capture(child):
                board.move(child)
                score = -self.quiescence(board, -beta, -alpha, -color, moves)
                board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

        return alpha

#  --------------------------------------------------------------------------------
#                       Sort moves for Negamax
#  --------------------------------------------------------------------------------

    def sort_moves(self, board, children, depth):

        # MVV sorting
        children.sort(key=lambda x: self.rate(board, x))

        # Killer moves
        if self.killer_moves[depth]:
            for move in self.killer_moves[depth]:
                if move in children:
                    children.remove(move)
                    children.append(move)

        # Best move from previous iteration is picked as best guess for next iteration
        key = chess.polyglot.zobrist_hash(board)
        if key in self.tt_entry:
            previous_best = self.tt_entry[key]['best move']
            if previous_best in children:
                children.remove(previous_best)
                children.append(previous_best)

        return children

    def rate(self, board, move):
        if board.is_capture(move):
            if board.is_en_passant(move):
                return 0  # pawn value (1) - pawn value (1) = 0
            else:
                return (board.piece_at(move.to_square).piece_type - board.piece_at(move.from_square).piece_type) * 100

        if move.promotion:
            return 0

        return -1000