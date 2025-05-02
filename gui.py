from __future__ import annotations
from typing import Callable

import json
import pygame

from gamestate import GameState, GameStatus, Action, Grid, GRID_SIZE
from theme import Theme, SIZE

type Coordinate = tuple[int, int]

PADDING_SMALL = 16
TILE_SIZE = 64


def load_theme(fn: str):
    with open(fn, "r") as fin:
        return json.load(fin)


class Button:
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        w: int = 2 * TILE_SIZE,
        h: int = TILE_SIZE,
        color: str = "black",
        text: str = "Click me!",
        light_text: bool = True,
        font_size: SIZE = SIZE.MEDIUM,
        onclick: Callable[[], None] = lambda: None,
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text = text
        self.light_text = light_text
        self.font_size = font_size
        self.onclick = onclick

    def draw(self, surface: pygame.Surface, theme: Theme) -> pygame.Rect:
        button = pygame.draw.rect(
            surface=surface,
            color=self.color,
            rect=self.rect,
            border_radius=theme.radius,
        )
        text_color = theme.light_text if self.light_text else theme.dark_text
        text = theme.font[self.font_size].render(self.text, True, text_color)
        text_pos = text.get_rect(center=button.center)
        surface.blit(text, text_pos)

        return button


class Board:
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        tile_size: int = TILE_SIZE,
        padding: int = PADDING_SMALL,
    ):
        self.padding = padding
        self.tile_size = tile_size
        size = GRID_SIZE * self.tile_size + (GRID_SIZE + 1) * self.padding
        self.rect = pygame.Rect(x, y, size, size)

    def _tile_rect(self, i: int, j: int):
        return pygame.Rect(
            self.rect.x + self.padding + (j * (self.tile_size + self.padding)),
            self.rect.y + self.padding + (i * (self.tile_size + self.padding)),
            self.tile_size,
            self.tile_size,
        )

    def draw(self, surface: pygame.Surface, theme: Theme, grid: Grid) -> pygame.Rect:
        # Draw board
        board = pygame.draw.rect(
            surface=surface,
            color=theme.board,
            rect=self.rect,
            border_radius=theme.radius,
        )

        # Draw tiles
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if grid[i][j] == 0:
                    tile_color = theme.blank_tile
                else:
                    tile_color, text_color = theme[grid[i][j]]
                tile = pygame.draw.rect(
                    surface=surface,
                    color=tile_color,
                    rect=self._tile_rect(i, j),
                    border_radius=theme.radius,
                )

                # Text
                if grid[i][j]:
                    text = theme.font_medium.render(str(grid[i][j]), True, text_color)
                    text_pos = text.get_rect(centerx=tile.centerx, centery=tile.centery)
                    surface.blit(text, text_pos)

        return board


class ScoreBoard:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(
        self, surface: pygame.Surface, theme: Theme, score: int = 0
    ) -> pygame.Rect:
        score_board = pygame.draw.rect(
            surface=surface,
            color=theme.board,
            rect=self.rect,
            border_radius=theme.radius,
        )
        text = theme.font_medium.render(str(score), True, theme.light_text)
        text_pos = text.get_rect(center=score_board.center)
        surface.blit(text, text_pos)
        return score_board


class GameOverScreen:
    def __init__(self, x=0, y=0, w=TILE_SIZE * 3, h=TILE_SIZE):
        self.rect = pygame.Rect(x, y, w, h)
        self.message_box = pygame.Surface((w, h))

    def draw(self, surface: pygame.Surface, theme: Theme) -> pygame.Rect:
        opacity_mask = pygame.Surface(surface.get_size())
        opacity_mask.fill((50, 50, 50))
        opacity_mask.set_alpha(150)
        surface.blit(opacity_mask, (0, 0))

        self.message_box.set_colorkey((0, 0, 0))
        pygame.draw.rect(
            self.message_box,
            theme.board,
            self.message_box.get_rect(),
            border_radius=theme.radius,
        )

        game_over_message = theme.font_medium.render(
            "Game Over!", True, theme.light_text
        )
        local_pos = game_over_message.get_rect(
            center=self.message_box.get_rect().center
        )
        self.message_box.blit(game_over_message, local_pos)

        global_pos = self.message_box.get_rect(center=surface.get_rect().center)
        surface.blit(self.message_box, global_pos)

        return global_pos


class GameGUI:
    def __init__(self, theme: Theme | None = None, tile_size: int = TILE_SIZE):
        if theme:
            self.theme = theme
        else:
            self.theme = Theme(
                radius=tile_size // 8,
                padding_small=tile_size // 4,
                padding_medium=tile_size // 2,
                padding_large=tile_size,
                font_size_small=tile_size // 8,
                font_size_medium=tile_size // 4,
                font_size_large=tile_size // 2,
            )

        self.game_state = GameState()

        self.board = Board(tile_size=tile_size, padding=self.theme.padding_small)
        self.score_board = ScoreBoard(
            int(0.5 * self.board.rect.width),
            self.theme.padding_small,
            int(0.4 * self.board.rect.width),
            tile_size,
        )
        self.board.rect.y = self.score_board.rect.bottom + PADDING_SMALL

        self.game_over_screen = GameOverScreen(w=tile_size * 3, h=tile_size)
        self.replay_button = Button(
            w=2 * tile_size,
            h=tile_size,
            color=theme.blank_tile,
            text="Replay",
            light_text=True,
            font_size=SIZE.MEDIUM,
            onclick=self.game_state.reset,
        )

        self.rect = pygame.Rect(0, 0, self.board.rect.right, self.board.rect.bottom)

    def draw(self, surface: pygame.Surface, theme: Theme) -> pygame.Rect:
        surface.fill(theme.bg)
        self.score_board.draw(surface, theme, self.game_state.score)
        self.board.draw(surface, theme, self.game_state.grid)
        if self.game_state.status == GameStatus.END:
            game_over_pos = self.game_over_screen.draw(surface, theme)
            game_over_pos.y += game_over_pos.h + theme.padding_small
            self.replay_button.rect.center = game_over_pos.center
            self.replay_button.draw(surface, theme)

    def event_handler(self, event: pygame.event.Event) -> None:
        if self.game_state.status == GameStatus.RUN:
            if event.type == pygame.KEYDOWN:
                key: int = event.key
                match key:
                    case pygame.K_LEFT:
                        # print("left")
                        state = self.game_state.step(Action.LEFT)
                    case pygame.K_RIGHT:
                        # print("right")
                        state = self.game_state.step(Action.RIGHT)
                    case pygame.K_UP:
                        # print("up")
                        state = self.game_state.step(Action.UP)
                    case pygame.K_DOWN:
                        # print("down")
                        state = self.game_state.step(Action.DOWN)
                    case _:
                        pass
                if state == GameStatus.END:
                    print(f"Game Over! Your score: {self.game_state.score}")
        if self.game_state.status == GameStatus.END:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button: int = event.button
                mouse_coor: Coordinate = event.pos
                if mouse_button == pygame.BUTTON_LEFT and self.replay_button.rect.collidepoint(mouse_coor):
                    self.replay_button.onclick()
