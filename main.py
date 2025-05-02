# Author: Nam Bui
# Date: 2025-04-26

from __future__ import annotations
import pygame

from gamestate import GameState, Action, GameStatus
from theme import Theme
from gui import Board, ScoreBoard, GameOverScreen, GameGUI

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
    theme = Theme(font_size_medium=32, font_size_large=64, padding_small=PADDING_SMALL)
    gui = GameGUI(theme=theme, tile_size=TILE_SIZE)
    # game_state.set_grid([[2, 4, 16, 64], [4, 2, 32, 32], [2, 4, 16, 64], [8, 2, 4, 8]])

    window_size = gui.rect.size
    screen = pygame.display.set_mode(window_size)

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            gui.event_handler(event)

        # fill the screen with a color to wipe away anything from last frame
        screen.fill(theme.bg)

        # RENDER YOUR GAME HERE
        gui.draw(screen, theme)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(15)  # limits FPS to 30

    pygame.quit()


if __name__ == "__main__":
    main()
