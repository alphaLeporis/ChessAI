import time

import chess.polyglot
import chess.gaviota

import project.chess_helpers.opening_move as om
import project.chess_helpers.endgame_move as em
import project.chess_helpers.parameters as pa
import project.chess_helpers.move_rate as mr
import project.chess_helpers.board_phase as bp
from project.chess_agents.agent import Agent
from project.chess_utilities.utility import *

start_time = 0
max_time = 0
ttable = {}


class NegaMaxQueiscence(Agent):

    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move-0.1)
        self.name = "NegaMax - Queiscence - MTDf - Opening - Closing"
        self.author = "Alexander, Louis, Niels"

        self.is_in_opening = True


    def calculate_move(self, board: chess.Board):
        move = None
        start_time = time.time()

        if self.is_in_opening and pa.OPENING_BOOK:
            time_start = time.time()
            move = om.make_opening_move(board)
            self.timer = time.time() - time_start
            if not move:
                self.is_in_opening = False

        if not self.is_in_opening or not pa.OPENING_BOOK:
            if (sum(board.piece_map()) <= 5) and pa.ENDGAME_BOOK:
                endgame_move, evaluation, dtz = em.find_endgame_move(board)
                if endgame_move:
                    print("This took: " + str(time.time() - start_time))
                    return endgame_move

            move = self.iterative_deepening(board)[0]

            if board.is_irreversible(move):  # Reset transposition table
                ttable.clear()
        print("This took: " + str(time.time() - start_time))
        return move

    def iterative_deepening(self, board):
        best_move = None
        guess = 0
        start_time = time.time()
        depth = 1
        while (time.time() < start_time + self.time_limit_move):
            move, guess, canceled = self.MTDf(board, depth, guess, self.time_limit_move - (time.time() - start_time))
            if not canceled:
                best_move = move
            depth += 1
        print("Hoe diep zitten we: " + str(depth))
        if not best_move:
            best_move = list(board.legal_moves)[0]
        return (best_move, guess)

    def MTDf(self, board, depth, guess, max_time):
        """
        Searches the possible moves using negamax by zooming in on the window
        Psuedocode from Aske Plaat, Jonathan Schaeffer, Wim Pijls, and Arie de Bruin
        """
        upperbound = pa.MATE_SCORE
        lowerbound = -pa.MATE_SCORE
        start_time = time.time()
        canceled = False
        move = None

        while (lowerbound < upperbound):
            if (time.time() - start_time > max_time):
                break
            if guess == lowerbound:
                beta = guess + 1
            else:
                beta = guess

            move, guess, canceled = self.negamax(board, depth, beta - 1, beta, max_time - (time.time() - start_time))

            if guess < beta:
                upperbound = guess
            else:
                lowerbound = guess

        return (move, guess, canceled)

    def negamax(self, board, depth, alpha, beta, max_time):
        start_time = time.time()
        key = chess.polyglot.zobrist_hash(board)
        tt_move = None
        tt_score = None
        canceled = False

        # Search for position in the transposition table
        if key in ttable:
            tt_depth, tt_move, tt_lowerbound, tt_upperbound = ttable[key]
            if tt_depth >= depth:
                if tt_upperbound <= alpha or tt_lowerbound == tt_upperbound:
                    return (tt_move, tt_upperbound, canceled)
                if tt_lowerbound >= beta:
                    return (tt_move, tt_lowerbound, canceled)

        if depth <= 0 or board.is_game_over():
            score = self.QuiescenceSearch(board, alpha, beta)
            ttable[key] = (depth, None, score, score)
            return (None, score, canceled)
        else:
            if self.do_null_move(board):
                board.push(chess.Move.null())
                null_move_depth_reduction = 2
                score = -self.negamax(board, depth - null_move_depth_reduction - 1, -beta, -beta + 1,
                                      max_time - (time.time() - start_time))[1]
                board.pop()
                if score >= beta:
                    return (None, score, canceled)

            # Alpha-beta negamax
            score = 0
            best_move = None
            best_score = -pa.INF
            moves = list(board.legal_moves)
            moves.sort(key=lambda move: mr.rate(board, move, tt_move), reverse=True)

            moves_searched = 0
            failed_high = False

            for move in moves:
                if (time.time() - start_time > max_time):
                    canceled = True
                    print("Is cancelled")
                    break
                board.push(move)
                full_depth_moves_threshold = 4
                reduction_threshold = 4
                late_move_depth_reduction = 1
                if moves_searched >= full_depth_moves_threshold and failed_high == False and depth >= reduction_threshold and self.reduction_ok(
                        board, move):
                    score = -self.negamax(board, depth - 1 - late_move_depth_reduction, -beta, -alpha,
                                          max_time - (time.time() - start_time))[1]
                else:
                    score = -self.negamax(board, depth - 1, -beta, -alpha, max_time - (time.time() - start_time))[1]
                board.pop()

                moves_searched += 1

                if score > best_score:
                    best_move = move
                    best_score = score

                # if (time.time() - start_time > max_time):
                #    return (best_move, best_score)

                alpha = max(alpha, best_score)

                if best_score >= beta:  # Beta cut-off (fails high)
                    failed_high = True
                    if not board.is_capture(move):
                        pa.htable[board.piece_at(move.from_square).color][move.from_square][
                            move.to_square] += depth ** 2  # Update history heuristic table
                    break

            # # Add position to the transposition table
            if best_score <= alpha:
                ttable[key] = (depth, best_move, -pa.MATE_SCORE, best_score)
            if alpha < best_score < beta:
                ttable[key] = (depth, best_move, best_score, best_score)
            if best_score >= beta:
                ttable[key] = (depth, best_move, best_score, pa.MATE_SCORE)

            return (best_move, best_score, canceled)

    def QuiescenceSearch(self, board, alpha, beta):
        global start_time
        global max_time
        # key = chess.polyglot.zobrist_hash(board)

        tt_move = None
        tt_score = None

        # Search for position in the transposition table
        # if key in ttable:
        #    tt_depth, tt_move, tt_lowerbound, tt_upperbound, tt_score = ttable[key]
        #    if tt_depth >= depth+4:
        #        if tt_upperbound <= alpha or tt_lowerbound == tt_upperbound:
        #            return tt_upperbound
        #        if tt_lowerbound >= beta:
        #            return tt_lowerbound

        bestValue = self.utility.board_value(board)
        if bestValue >= beta:
            return beta
        if (alpha < bestValue):
            alpha = bestValue

        if (alpha >= beta or board.is_game_over()):
            return bestValue

        best_move = None

        favorable_moves = []
        for move in list(board.legal_moves):
            if self.is_favorable_move(board, move):
                favorable_moves.append(move)
        if (favorable_moves != []):
            favorable_moves.sort(key=lambda move: mr.rate(board, move, tt_move), reverse=True)
        for move in favorable_moves:
            board.push(move)
            value = -1 * self.QuiescenceSearch(board, -beta, -alpha)
            #
            key = chess.polyglot.zobrist_hash(board)
            ttable[key] = (0, None, value, value)
            board.pop()

            # if value > bestValue:
            #     bestValue = value

            if value >= beta:
                return beta

            # bestValue = max(bestValue, value)

            alpha = max(alpha, value)

        return alpha

    def is_favorable_move(self, board: chess.Board, move: chess.Move) -> bool:
        if move.promotion is not None:
            return True
        if board.is_capture(move) and not board.is_en_passant(move):
            if pa.piece_values.get(board.piece_type_at(move.from_square)) < pa.piece_values.get(
                    board.piece_type_at(move.to_square)
            ) or len(board.attackers(board.turn, move.to_square)) > len(
                board.attackers(not board.turn, move.to_square)
            ):
                return True
        return False

    def do_null_move(self, board):
        """
        Returns true if conditions are met to perform null move pruning
        Returns false if side to move is in check or it's the endgame (because position is possibly zugzwang)
        """
        endgame_threshold = 100
        if (board.ply() >= 1 and board.peek() != chess.Move.null()) or board.is_check() or bp.get_phase(
                board) >= endgame_threshold:
            return False
        return True

    def set_ttable(self, board, move):
        """
        Clear the transposition table after an irreversible move (pawn moves, captures, etc)
        """
        if move:
            if board.is_irreversible(move):
                ttable.clear()

    def reduction_ok(self, board, move):
        """
        Returns true if conditions are met to perform late move reduction
        Returns false if move:
        - Is a capture
        - Is a promotion
        - Gives check
        - Is made while in check
        """
        result = True
        board.pop()
        if board.is_capture(move) or move.promotion or board.gives_check(move) or board.is_check():
            result = False
        board.push(move)
        return result
