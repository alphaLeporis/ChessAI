import project.chess_helpers.parameters as pa


def rate(board, move, tt_move):
    """
    Rates a move in relation to the following order for move ordering:
    - Refutation move (moves from transpositions) | score = 6
    - Winning captures (low value piece captures high value piece) | 1 <= score <= 5
    - Promotions / Equal captures (piece captured and capturing have the same value) | score = 0
    - Losing captures (high value piece captures low value piece) | -5 <= score <= -1
    - All others | score = -100
    Pieces have the following values:
    - Pawn: 1
    - Knight: 2
    - Bishop: 3
    - Rook: 4
    - Queen: 5
    - King: 6

    :param board: the state of the board right now.
    :param move: the move in question.
    :param tt_move: if the move is from the TT table.
    :return: arbitrary value, and only useful when comparing whether
    one is higher or lower than the other
    """
    if tt_move:
        return 600

    if pa.htable[board.piece_at(move.from_square).color][move.from_square][move.to_square] != 0:
        return pa.htable[board.piece_at(move.from_square).color][move.from_square][move.to_square] / -100

    if board.is_capture(move):
        if board.is_en_passant(move):
            return 0  # pawn value (1) - pawn value (1) = 0
        else:
            return (board.piece_at(move.to_square).piece_type - board.piece_at(move.from_square).piece_type) * 100

    if move.promotion:
        return 0

    return -1000
