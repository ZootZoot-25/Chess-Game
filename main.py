import ai
import pygame
import chess
import sys

# Constants
BOARD_WIDTH, HEIGHT = 640, 640
UI_WIDTH = 200
WIDTH = BOARD_WIDTH + UI_WIDTH
DIMENSION = 8
SQ_SIZE = BOARD_WIDTH // DIMENSION
FPS = 60

IMAGES = {}

def load_images():
    pieces = ['blackRook', 'blackKnight', 'blackBishop', 'blackQueen', 'blackKing', 'blackPawn',
              'whiteRook', 'whiteKnight', 'whiteBishop', 'whiteQueen', 'whiteKing', 'whitePawn']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(f"assets/{piece}.png"), (SQ_SIZE, SQ_SIZE)
        )

def draw_board(screen):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board, dragged_square=None):
    symbol_to_image = {
        'r': 'blackRook', 'n': 'blackKnight', 'b': 'blackBishop', 'q': 'blackQueen', 'k': 'blackKing', 'p': 'blackPawn',
        'R': 'whiteRook', 'N': 'whiteKnight', 'B': 'whiteBishop', 'Q': 'whiteQueen', 'K': 'whiteKing', 'P': 'whitePawn'
    }
    for square in chess.SQUARES:
        if square == dragged_square:
            continue
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)
            col = square % 8
            image_key = symbol_to_image[piece.symbol()]
            screen.blit(IMAGES[image_key], pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def get_square_under_mouse():
    x, y = pygame.mouse.get_pos()
    col = x // SQ_SIZE
    row = y // SQ_SIZE
    return chess.square(col, 7 - row)

def draw_button(screen, rect, text, font):
    pygame.draw.rect(screen, pygame.Color("darkgray"), rect)
    pygame.draw.rect(screen, pygame.Color("black"), rect, 2)
    text_surf = font.render(text, True, pygame.Color("black"))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def highlight_square(screen, square, color):
    row = 7 - (square // 8)
    col = square % 8
    highlight_rect = pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
    pygame.draw.rect(screen, pygame.Color(color), highlight_rect, 4)

def main():
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Chess with AI and Hint")

    load_images()
    board = chess.Board()
    dragging = False
    dragged_piece = None
    drag_start_square = None
    drag_position = None
    hint_move = None

    while True:
        screen.fill(pygame.Color("lightgray"))
        draw_board(screen)

        if hint_move and board.turn == chess.WHITE and not board.is_game_over():
            highlight_square(screen, hint_move.from_square, "green")
            highlight_square(screen, hint_move.to_square, "green")

        draw_pieces(screen, board, drag_start_square if dragging else None)

        if dragging and dragged_piece and drag_position:
            image_key = {
                'r': 'blackRook', 'n': 'blackKnight', 'b': 'blackBishop', 'q': 'blackQueen',
                'k': 'blackKing', 'p': 'blackPawn', 'R': 'whiteRook', 'N': 'whiteKnight',
                'B': 'whiteBishop', 'Q': 'whiteQueen', 'K': 'whiteKing', 'P': 'whitePawn'
            }[dragged_piece.symbol()]
            image = IMAGES[image_key]
            rect = image.get_rect(center=drag_position)
            screen.blit(image, rect)

        pygame.draw.line(screen, pygame.Color("black"), (BOARD_WIDTH, 0), (BOARD_WIDTH, HEIGHT), 2)

        turn_text = "PLAYER TURN" if board.turn == chess.WHITE else "AI TURN"
        screen.blit(font.render(turn_text, True, pygame.Color("black")), (BOARD_WIDTH + 20, 30))

        reset_button = pygame.Rect(BOARD_WIDTH + 20, 100, 160, 40)
        exit_button = pygame.Rect(BOARD_WIDTH + 20, 160, 160, 40)
        hint_button = pygame.Rect(BOARD_WIDTH + 20, 220, 160, 40)

        draw_button(screen, reset_button, "Reset Game", font)
        draw_button(screen, hint_button, "Show Hint", font)

        if board.is_game_over():
            if board.is_checkmate():
                result = f"{'White' if board.turn == chess.BLACK else 'Black'} wins by checkmate"
            elif board.is_stalemate():
                result = "Draw by stalemate"
            else:
                result = "Game over"
            screen.blit(font.render(result, True, pygame.Color("red")), (BOARD_WIDTH + 20, 70))
            draw_button(screen, exit_button, "Exit Game", font)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if reset_button.collidepoint(mouse_pos):
                    board = chess.Board()
                    dragging = False
                    dragged_piece = None
                    drag_start_square = None
                    drag_position = None
                    hint_move = None

                elif hint_button.collidepoint(mouse_pos) and board.turn == chess.WHITE and not board.is_game_over():
                    hint_move = ai.select_best_move(board, depth=2)

                elif board.is_game_over() and exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

                elif mouse_pos[0] < BOARD_WIDTH and not dragging:
                    square = get_square_under_mouse()
                    piece = board.piece_at(square)
                    if board.turn == chess.WHITE and piece and piece.color == chess.WHITE:
                        dragging = True
                        dragged_piece = piece
                        drag_start_square = square
                        drag_position = mouse_pos

            elif event.type == pygame.MOUSEMOTION and dragging:
                drag_position = pygame.mouse.get_pos()

            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                drop_square = get_square_under_mouse()
                move = chess.Move(drag_start_square, drop_square)

                # Prevent selecting another piece while dragging
                if drop_square != drag_start_square:
                    if board.piece_at(drag_start_square).piece_type == chess.PAWN and chess.square_rank(drop_square) in [0, 7]:
                        move = chess.Move(drag_start_square, drop_square, promotion=chess.QUEEN)

                    if board.turn == chess.WHITE and move in board.legal_moves:
                        board.push(move)
                        hint_move = None

                        if board.turn == chess.BLACK and not board.is_game_over():
                            ai_move = ai.select_best_move(board, depth=3)
                            if ai_move:
                                board.push(ai_move)

                dragging = False
                dragged_piece = None
                drag_start_square = None
                drag_position = None

    pygame.quit()

if __name__ == "__main__":
    main()