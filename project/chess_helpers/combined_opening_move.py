import chess
import chess.polyglot
import random
import os
import time


def make_opening_move(board):

    moves = []
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../data/opening_book')
    for subdir, dirs, files in os.walk(filename):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            if ext in '.bin':
                with chess.polyglot.open_reader(os.path.join(subdir, file)) as reader:
                    for i, entry in enumerate(reader.find_all(board)):
                        moves.append(entry.move)

                        # Only pick from the most common openings
                        if i == 2:
                            break

    # Pick a random move if exists, else return None
    if moves:
        random_move = random.choice(moves)
    else:
        return None

    # Convert the move to the right format

    # Wait for some time just so simulate the AI "thinking" during openings
    time.sleep(random.uniform(0.5, 1.5))

    return random_move
