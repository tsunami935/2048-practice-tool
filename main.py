# Author: Nam Bui
# Date: 2025-04-26

from __future__ import annotations
import pygame

from gamestate import GameState, Action, GameStatus
from theme import Theme
from gui import Board, ScoreBoard, GameOverScreen

TILE_SIZE = 64
PADDING_SMALL = 16


class GameInterface:
    def __init__(self):
        pass


def main():
    # pygame setup
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()
    running = True
    

    # Game objects
    theme = Theme(font_size_medium=32, font_size_large=64)
    board = Board(tile_size=TILE_SIZE)
    score_board = ScoreBoard(
        int(0.5 * board.rect.width),
        PADDING_SMALL,
        int(0.4 * board.rect.width),
        TILE_SIZE,
    )
    board.rect.y = score_board.rect.bottom + PADDING_SMALL
    game_state = GameState()
    # game_state.set_grid([[2, 4, 16, 64], [4, 2, 32, 32], [2, 4, 16, 64], [8, 2, 4, 8]])

    window_size = (board.rect.right, board.rect.bottom)
    screen = pygame.display.set_mode(window_size)
    game_over = GameOverScreen()

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state.status == GameStatus.RUN:
                if event.type == pygame.KEYDOWN:
                    key: int = event.key
                    match key:
                        case pygame.K_LEFT:
                            # print("left")
                            state = game_state.step(Action.LEFT)
                        case pygame.K_RIGHT:
                            # print("right")
                            state = game_state.step(Action.RIGHT)
                        case pygame.K_UP:
                            # print("up")
                            state = game_state.step(Action.UP)
                        case pygame.K_DOWN:
                            # print("down")
                            state = game_state.step(Action.DOWN)
                        case _:
                            pass
                    if state == GameStatus.END:
                        print(f"Game Over! Your score: {game_state.score}")

        # fill the screen with a color to wipe away anything from last frame
        screen.fill(theme.bg)

        # RENDER YOUR GAME HERE
        score_board.draw(screen, theme, game_state.score)
        board.draw(screen, theme, game_state.grid)
        if game_state.status == GameStatus.END:
            game_over.draw(screen, theme)


        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(15)  # limits FPS to 30

    pygame.quit()


if __name__ == "__main__":
    main()
