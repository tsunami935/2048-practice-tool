from __future__ import annotations
from typing import TextIO, Any

import json
from enum import StrEnum

from pygame.font import Font
from pygame import Color

class SIZE(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class TileTheme:
    """Data class for tile theme."""
    def __init__(self, color: str = "beige", light: bool = False):
        self.tile_color = color
        self.light = light

class Theme:
    """Appearance settings class."""
    def __init__(
        self,
        bg: str = "azure",
        board: str = "burlywood4",
        blank_tile: str = "cornsilk4",
        radius: int = 8,
        padding_small: int = 16,
        padding_medium: int = 32,
        padding_large: int = 64,
        font: str = "fonts/ClearSans-Medium.ttf",
        font_size_small: int = 8,
        font_size_medium: int = 16,
        font_size_large: int = 32,
        light_text: str = "azure",
        dark_text: str = "burlywood4",
        tiles: dict[int, TileTheme] = {
            2: TileTheme("beige"),
            4: TileTheme("antiquewhite"),
            8: TileTheme("peachpuff1", True),
            16: TileTheme("orange", True),
            32: TileTheme("orangered", True),
            64: TileTheme("orangered3", True),
            128: TileTheme("khaki", True),
            256: TileTheme("khaki1", True),
            512: TileTheme("gold", True),
            1024: TileTheme("gold1", True),
            2048: TileTheme("goldenrod1", True),
            0: TileTheme("black", True)
        },
    ) -> None:
        self.bg = bg
        self.board = board
        self.blank_tile = blank_tile
        self.radius = radius
        self.padding_small = padding_small
        self.padding_medium = padding_medium
        self.padding_large = padding_large
        self.font_small = Font(font, font_size_small)
        self.font_medium = Font(font, font_size_medium)
        self.font_large = Font(font, font_size_large)
        self.font = {
            SIZE.SMALL: self.font_small,
            SIZE.MEDIUM: self.font_medium,
            SIZE.LARGE: self.font_large
        }
        self.light_text = light_text
        self.dark_text = dark_text
        self.tiles = tiles

    def __getitem__(self, tile) -> tuple[Color, Color]:
        """Get tile and text color of a given tile."""
        if tile > 2048:
            tile = 0
        theme = self.tiles[tile]
        text_color = self.light_text if theme.light else self.dark_text
        return theme.tile_color, text_color

    def load(file: TextIO) -> Theme:
        """Load theme from file."""
        data: dict[str, Any] = json.load(file)
        raise NotImplementedError

    def dump(self, file: TextIO) -> None:
        """Write theme to file."""
        raise NotImplementedError
