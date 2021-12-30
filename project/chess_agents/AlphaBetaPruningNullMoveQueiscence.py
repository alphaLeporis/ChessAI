import os
import time

import chess
import chess.polyglot
import chess.gaviota

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

        # return negamax(board, depth, -MATE_SCORE, MATE_SCORE)[0]
        # return MTDf(board, depth, 0)[0]
        #return negacstar(board, depth, -MATE_SCORE, MATE_SCORE)[0]
        move = self.iterative_deepening(board)[0]
        print("This took: "+ str(time.time() - start_time))
        return move

    def iterative_deepening(self, board):
        """
        Approaches the desired depth in steps using MTD(f)
        """

        guess = 0
        start_time = time.time()
        depth = 1
        while (time.time() < start_time + self.time_limit_move):
            move, guess = negacstar(board, depth, -MATE_SCORE, MATE_SCORE, self.time_limit_move-(time.time()-start_time))
            depth += 1
        return (move, guess)


def negamax(board, depth, alpha, beta):
    """
    Searches the possible moves using negamax, alpha-beta pruning, null-move pruning, and a transposition table
    Initial psuedocode adapated from Jeroen W.T. Carolus
    TODO
    - killer heuristic
    - null move pruning
    - history heuristic
    - legal move generation (bitboards)
    - late move reduction
    - https://www.chessprogramming.org/Search#Alpha-Beta_Enhancements
    - parallel search
    - extensions
    - aspiration search?
    - Quiescence Search (doesnt work)
    """
    key = chess.polyglot.zobrist_hash(board)
    tt_move = None
    global start_time
    global max_time

    # Search for position in the transposition table
    if key in ttable:
        tt_move, tt_lowerbound, tt_upperbound, tt_depth = ttable[key]
        if tt_depth >= depth:
            if tt_upperbound <= alpha or tt_lowerbound == tt_upperbound:
                return (tt_move, tt_upperbound)
            if tt_lowerbound >= beta:
                return (tt_move, tt_lowerbound)

    if depth == 0 or board.is_game_over():
        score = QuiescenceSearch(board, alpha, beta, 3)
        ttable[key] = (None, score, score, depth)  # Add position to the transposition table
        return (None, score)
    else:
        # Alpha-beta negamax
        score = 0
        best_move = None
        best_score = -INF
        moves = list(board.legal_moves)
        moves.sort(key=lambda move: rate(board, move, tt_move), reverse=True)

        for move in moves:
            board.push(move)
            score = -negamax(board, depth - 1, -beta, -alpha)[1]
            board.pop()


            if score > best_score:
                best_move = move
                best_score = score

            alpha = max(alpha, best_score)

            if alpha >= beta:  # Beta cut-off
                break

        # # Add position to the transposition table
        if best_score <= alpha:
            ttable[key] = (best_move, -MATE_SCORE, best_score, depth)
        if alpha < best_score < beta:
            ttable[key] = (best_move, best_score, best_score, depth)
        if best_score >= beta:
            ttable[key] = (best_move, best_score, MATE_SCORE, depth)

        return (best_move, best_score)


def MTDf(board, depth, guess):
    """
    Searches the possible moves using negamax by zooming in on the window
    Psuedocode and algorithm from Aske Plaat, Jonathan Schaeffer, Wim Pijls, and Arie de Bruin
    """
    upperbound = MATE_SCORE
    lowerbound = -MATE_SCORE
    while (lowerbound < upperbound):
        if guess == lowerbound:
            beta = guess + 1
        else:
            beta = guess

        move, guess = negamax(board, depth, beta - 1, beta)

        if guess < beta:
            upperbound = guess
        else:
            lowerbound = guess

    return (move, guess)


def negacstar(board, depth, mini, maxi, max_time):
    """
    Searches the possible moves using negamax by zooming in on the window
    Pseudocode and algorithm from Jean-Christophe Weill
    """
    start_time = time.time()
    while (mini < maxi):
        if (time.time()-start_time > max_time):
            break
        alpha = (mini + maxi) / 2
        move, score = negamax(board, depth, alpha, alpha + 1)
        if score > alpha:
            mini = score
        else:
            maxi = score
    return (move, score)



def QuiescenceSearch( board, alpha, beta, depth):
        flip_value = 1 if board.turn == chess.WHITE else -1

        bestValue = flip_value * evaluate(board)

        alpha = max(alpha, bestValue)

        if (alpha >= beta or depth == 0):
            return bestValue

        favorable_moves = []
        for move in list(board.legal_moves):
            if is_favorable_move(board, move):
                favorable_moves.append(move)
        for move in favorable_moves:
            board.push(move)
            value = -1 * QuiescenceSearch(board, -beta, -alpha, depth-1)
            board.pop()

            bestValue = max(bestValue, value)

            alpha = max(alpha, bestValue)

            if (alpha >= beta):
                break
        return bestValue

piece_values = {
        chess.BISHOP: 330,
        chess.KING: 20_000,
        chess.KNIGHT: 320,
        chess.PAWN: 100,
        chess.QUEEN: 900,
        chess.ROOK: 500,
    }

def is_favorable_move(board: chess.Board, move: chess.Move) -> bool:
        if move.promotion is not None:
            return True
        if board.is_capture(move) and not board.is_en_passant(move):
            if piece_values.get(board.piece_type_at(move.from_square)) < piece_values.get(
                    board.piece_type_at(move.to_square)
            ) or len(board.attackers(board.turn, move.to_square)) > len(
                board.attackers(not board.turn, move.to_square)
            ):
                return True
        return False