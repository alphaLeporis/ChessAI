import os
import time

import chess
import chess.polyglot
import chess.gaviota
from joblib import Parallel, delayed

from project.chess_agents.agent import Agent
from project.chess_utilities.NewUtility import *

start_time = 0
max_time = 0
ttable = {}

class AlphaBetaPruningNullMoveQueiscence(Agent):

    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move)
        self.name = "Best Agent Ever"
        self.author = "Alexander, Louis, Niels"

        self.best_move = None
        self.best_score = 0

    def calculate_move(self, board: chess.Board):
        """
        Chooses a move for the CPU
        If inside opening book make book move
        If inside Gaviota tablebase make tablebase move
        Else search for a move
        """
        start_time = time.time()
        global OPENING_BOOK
        depth = 4

        if OPENING_BOOK:
            try:
                dir_path = os.path.dirname(os.path.realpath(__file__))
                with chess.polyglot.open_reader(
                        os.path.join(dir_path,
                                     "Opening_Book.bin")) as opening_book:  # https://sourceforge.net/projects/codekiddy-chess/files/
                    opening = opening_book.choice(board)
                    opening_book.close()
                    print("This took: " + str(time.time() - start_time))
                    return opening.move
            except IndexError:
                OPENING_BOOK = False

        move = self.iterative_deepening(board)[0]
        print("This took: "+ str(time.time() - start_time))
        self.set_ttable(board, move)
        return move

    def negamax(self, board, depth, alpha, beta, max_time):
        start_time = time.time()
        key = chess.polyglot.zobrist_hash(board)
        tt_move = None
        tt_score = None
        canceled = False

        # Search for position in the transposition table
        if key in ttable:
            tt_depth, tt_move, tt_lowerbound, tt_upperbound, tt_score = ttable[key]
            if tt_depth >= depth:
                if tt_upperbound <= alpha or tt_lowerbound == tt_upperbound:
                    return (tt_move, tt_upperbound, canceled)
                if tt_lowerbound >= beta:
                    return (tt_move, tt_lowerbound, canceled)

        if depth == 0 or board.is_game_over():
            score = self.QuiescenceSearch(board, alpha, beta, 3)
            ttable[key] = (depth, None, score, score, score)
            return (None, score, canceled)
        else:
            if self.do_null_move(board) and depth > 3:
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
            best_score = -INF
            moves = list(board.legal_moves)
            moves.sort(key=lambda move: rate(board, move, tt_move, tt_score), reverse=True)

            start_time2 = time.time()
            time_left = max_time - (time.time() - start_time2)

            Parallel(n_jobs=4)(delayed(self.alpha_beta_negamax)(board.copy(), move, depth, alpha, beta,start_time2, time_left) for move in moves)

            # # Add position to the transposition table
            if best_score <= alpha:
                ttable[key] = (depth, best_move, -MATE_SCORE, best_score, best_score)
            if alpha < best_score < beta:
                ttable[key] = (depth, best_move, best_score, best_score, best_score)
            if best_score >= beta:
                ttable[key] = (depth, best_move, best_score, MATE_SCORE, best_score)

            return (best_move, best_score, canceled)

    def alpha_beta_negamax(self, board, move, depth, alpha, beta, start_time, max_time):
        if (time.time() - start_time > max_time):
            canceled = True
            return
        board.push(move)
        score = -self.negamax(board, depth - 1, -beta, -alpha, max_time - (time.time() - start_time))[1]
        board.pop()

        if score > self.best_score:
            self.best_move = move
            self.best_score = score

        # if (time.time() - start_time > max_time):
        #    return (best_move, best_score)

        alpha = max(alpha, self.best_score)

        if alpha >= beta:  # Beta cut-off
            return


    def iterative_deepening(self, board):
        """
        Approaches the desired depth in steps using MTD(f)
        """
        final_move = None
        guess = 0
        start_time = time.time()
        depth = 1
        while (time.time() < start_time + self.time_limit_move):
            move, guess, canceled  = self.negacstar(board, depth, -MATE_SCORE, MATE_SCORE, self.time_limit_move-(time.time()-start_time))
            if not canceled:
                best_move = move
            depth += 1
        print("Hoe diep zitten we: " + str(depth))
        if not best_move:
            best_move = list(board.legal_moves)[0]
        return (best_move, guess)




    def negacstar(self, board, depth, mini, maxi, max_time):
        """
        Searches the possible moves using negamax by zooming in on the window
        Pseudocode and algorithm from Jean-Christophe Weill
        """
        start_time = time.time()
        while (mini < maxi):
            if (time.time()-start_time > max_time):
                break
            alpha = (mini + maxi) / 2
            move, score, canceled = self.negamax(board, depth, alpha, alpha + 1, max_time-(time.time()-start_time))

            if score > alpha:
                mini = score
            else:
                maxi = score
        return (move, score, canceled)


    def QuiescenceSearch(self, board, alpha, beta, depth):
        global start_time
        global max_time
        key = chess.polyglot.zobrist_hash(board)

        tt_move = None
        tt_score = None

         #Search for position in the transposition table
        if key in ttable:
            tt_depth, tt_move, tt_lowerbound, tt_upperbound, tt_score = ttable[key]
            if tt_depth >= depth+4:
                if tt_upperbound <= alpha or tt_lowerbound == tt_upperbound:
                    return tt_upperbound
                if tt_lowerbound >= beta:
                    return tt_lowerbound


        bestValue = evaluate(board)
        if bestValue >= beta:
            return beta
        alpha = max(alpha, bestValue)

        if (alpha >= beta or depth == 0 or board.is_game_over()):
            return bestValue

        best_move = None

        favorable_moves = []
        for move in list(board.legal_moves):
            if self.is_favorable_move(board, move):
                favorable_moves.append(move)
        if (favorable_moves != []):
            favorable_moves.sort(key=lambda move: rate(board, move, tt_move, tt_score), reverse=True)
        for move in favorable_moves:
            board.push(move)
            value = -1 * self.QuiescenceSearch(board, -beta, -alpha, depth - 1)
            key = chess.polyglot.zobrist_hash(board)
            ttable[key] = (0, None, value, value, value)
            board.pop()

            if value > bestValue:
                bestValue = value

            if value >= beta:
                return beta

            bestValue = max(bestValue, value)
            #if(time.time()-start_time>max_time):
            #    return bestValue
            alpha = max(alpha, bestValue)

        return alpha

    piece_values = {
        chess.BISHOP: 330,
        chess.KING: 20_000,
        chess.KNIGHT: 320,
        chess.PAWN: 100,
        chess.QUEEN: 900,
        chess.ROOK: 500,
    }

    def is_favorable_move(self, board: chess.Board, move: chess.Move) -> bool:
        if move.promotion is not None:
            return True
        if board.is_capture(move) and not board.is_en_passant(move):
            if self.piece_values.get(board.piece_type_at(move.from_square)) < self.piece_values.get(
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
        if board.is_check() or get_phase(board) >= endgame_threshold:
            return False
        return True

    def set_ttable(self, board, move):
        """
        Clear the transposition table after an irreversible move (pawn moves, captures, etc)
        """
        if move:
            if board.is_irreversible(move):
                ttable.clear()

