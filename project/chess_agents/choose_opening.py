import os

import chess.pgn

from project.chess_agents.opening.pgn_parser import file

class choose_opening():
    def __init__(self):
        """Setup the Search Agent"""
        self.parsedoutput = []
        pass

    def init(self, color: int):
        self.parse_data(color)

    def parse_data(self, color):
        with open('../data/lichess_db_standard_rated_2015-08.pgn', 'r') as f:
            self.parsedoutput = file.parse(f.read()).or_die()
        currentelement = 0
        expected_outcome = "1-0" if color == 1 else "0-1"
        while (currentelement < len(self.parsedoutput)):
            if (self.parsedoutput[currentelement]['game']['outcome'] == expected_outcome):
                self.parsedoutput.pop(currentelement)
            else:
                currentelement += 1
        print(len(self.parsedoutput))

    def iterate(self, board: chess.Board):
        print(board.move_stack[-1])



if __name__ == "__main__":
    choose_opening()
