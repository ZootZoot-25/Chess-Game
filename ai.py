import chess
import math

# Assign piece values for material evaluation
piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3.25,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0  # King's value is strategic, not direct
}

# Central squares for bonus
center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]

def evaluate_board(board):
    """
    Evaluate the board with:
    - Material count
    - Center control bonus for pawns
    - Mobility score
    - King safety (pawn shield)
    - Repetition penalty
    """
    value = 0

    # Material and center control
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            score = piece_values.get(piece.piece_type, 0)
            if piece.piece_type == chess.PAWN and square in center_squares:
                score += 0.1  # Encourage central control
            value += score if piece.color == chess.WHITE else -score

    # Mobility
    white_mobility = len([m for m in board.legal_moves if board.color_at(m.from_square) == chess.WHITE])
    board.push(chess.Move.null())  # simulate black's turn
    black_mobility = len([m for m in board.legal_moves if board.color_at(m.from_square) == chess.BLACK])
    board.pop()
    value += 0.05 * (white_mobility - black_mobility)

    # King safety
    white_king = board.king(chess.WHITE)
    black_king = board.king(chess.BLACK)
    if white_king:
        file = chess.square_file(white_king)
        shield = sum(1 for df in [-1, 0, 1] if 0 <= file + df < 8 and
                     board.piece_at(chess.square(file + df, 1)) == chess.Piece(chess.PAWN, chess.WHITE))
        value += 0.1 * shield
    if black_king:
        file = chess.square_file(black_king)
        shield = sum(1 for df in [-1, 0, 1] if 0 <= file + df < 8 and
                     board.piece_at(chess.square(file + df, 6)) == chess.Piece(chess.PAWN, chess.BLACK))
        value -= 0.1 * shield

    # Repetition penalty
    if board.is_repetition(2):
        value -= 0.5

    return value

def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Adversarial search using Minimax with Alpha-Beta pruning.
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def select_best_move(board, depth):
    """
    Select the best move for the AI (Black).
    Looks for the move that minimizes the board evaluation for White.
    """
    best_move = None
    best_value = math.inf

    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, -math.inf, math.inf, True)
        board.pop()
        if value < best_value:
            best_value = value
            best_move = move

    return best_move