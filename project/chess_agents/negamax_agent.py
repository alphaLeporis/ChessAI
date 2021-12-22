import os
import time
import chess
from math import inf
import chess.polyglot

from project.chess_agents.agent import Agent
from project.chess_utilities.utility import Utility


class NegamaxAgent(Agent):

    # Initialize your agent with whatever parameters you want
    def __init__(self, utility: Utility, time_limit_move: float) -> None:
        super().__init__(utility, time_limit_move)
        self.name = "Example search agent"
        self.author = "J. Duym & A. Troch"

        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            self.reader = chess.polyglot.open_reader(os.path.join(dir_path, 'book/book.bin'))
        except FileNotFoundError:
            print('No opening book found. make sure you have it in the right folder (path should be ..\\book.bin)')

    # This agent does not perform any searching, it sinmply iterates trough all the moves possible and picks the one with the highest utility
    def calculate_move(self, board: chess.Board):
        global positions
        color = 1 if board.turn == chess.WHITE else -1
        positions, depth = 0, 1
        bestMove = None
        value = 0
        start_time = time.time()
        while time.time() - start_time < self.time_limit_move-1:
            start_time2 = time.time()
            bestMove, value = self.negaMaxRoot(board, depth, -inf, inf, color, depth, self.time_limit_move- (time.time() - start_time)-0.5)
            print("Depth " + str(depth) + " took: " + str(time.time() - start_time2) + "s")
            depth += 1
        print("This took: "+str(time.time()-start_time)+"s")
        return bestMove

    def move(self, board, depth, color):
        global positions
        positions = 0
        # implementing the opening book + move analysis functions
        if self.reader:
            try:
                return self.reader.weighted_choice(board).move
            except IndexError:
                bestMove, value = self.negaMaxRoot(board, depth, -inf, inf, color, depth)
                return bestMove
        bestMove, value = self.negaMaxRoot(board, depth, -inf, inf, color, depth)
        return bestMove

    def negaMaxRoot(self, board, depth, alpha, beta, color, maxDepth, timeLeft):
        global positions
        positions += 1
        value = -inf
        moves = board.generate_legal_moves()
        bestMove = next(moves)
        start_time = time.time()
        for move in moves:
            if time.time() - start_time > timeLeft:
                break
            board.push(move)
            boardValue = -1 * self.negaMax(board, depth - 1, -beta, -alpha, -color, maxDepth)
            board.pop()
            if boardValue > value:
                value = boardValue
                bestMove = move
            # implementing alpha-beta cutoff
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return bestMove, value

    # Nega Max Child Call
    def negaMax(self, board, depth, alpha, beta, color, maxDepth):
        global positions
        positions += 1
        # draw and mate checking (values shallow mates more than deeper ones)
        if board.is_fivefold_repetition() or board.is_stalemate() or board.is_seventyfive_moves():
            return 0
        if board.is_checkmate():
            return color * (1 - (0.01 * (maxDepth - depth))) * -99999 if board.turn else color * (
                        1 - (0.01 * (maxDepth - depth))) * 99999
        # testing for 'noisy' positions, and quiescence searching them for Horizon effect mitigation
        if depth == 0:
            if board.is_capture(board.peek()) or board.is_check():
                return self.qSearch(board, alpha, beta, color, maxDepth)
            return color * self.utility.board_value(board)
        value = -inf
        moves = board.generate_legal_moves()
        for move in moves:
            board.push(move)
            value = max(value, -1 * self.negaMax(board, depth - 1, -beta, -alpha, -color, maxDepth))
            board.pop()
            # implementing alpha-beta cutoff
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value

    # starting the quiescence search code (only searches up to 4 ply extra from noisy moves)
    def qSearch(self, board, alpha, beta, color, startingDepth, depth=0, maxDepth=4):
        global positions
        positions += 1
        # mate test (values shallow mates more than deeper ones)
        if board.is_checkmate():
            return color * (1 - (0.01 * (startingDepth + depth))) * -99999 if board.turn else color * (
                        1 - (0.01 * (startingDepth + depth))) * 99999
        # get stand-pat for delta pruning
        value = color * self.utility.board_value(board)
        # alpha-beta cutoffs
        if value >= beta:
            return beta
        if alpha < value:
            alpha = value
        if depth < maxDepth:
            captureMoves = (move for move in board.generate_legal_moves() if
                            (board.is_capture(move) or board.is_check()))
            for move in captureMoves:
                board.push(move)
                score = -1 * self.qSearch(board, -beta, -alpha, -color, depth + 1, maxDepth)
                board.pop()
                # more alpha-beta cutoffs
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha
