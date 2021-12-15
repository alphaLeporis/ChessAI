import os

import chess.pgn

from project.chess_agents.opening.pgn_parser import file


def parse_data(color):
    with open('../data/lichess_carangelmx_2019-01-01.pgn', 'r') as f:
        parsedoutput = file.parse(f.read()).or_die()
    currentelement = 0
    expected_outcome = "1-0" if color == 1 else "0-1"
    while (currentelement < len(parsedoutput)):
        if (parsedoutput[currentelement]['game']['outcome'] == expected_outcome):
            parsedoutput.pop(currentelement)
        else:
            currentelement += 1
    print(parsedoutput)

def choose_openings():
    with open('../data/lichess_carangelmx_2019-01-01.pgn', 'r') as f:
        parsedoutput = file.parse(f.read()).or_die()
        print(len(parsedoutput))



if __name__ == "__main__":
    parse_data(1)