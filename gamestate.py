from __future__ import annotations
from typing import TextIO

from collections import deque, defaultdict
from enum import Enum, auto
from random import Random
import sys
import time

type Grid = list[list[int]]
type ActionMap = dict[Action, NextState]


class Action(Enum):
    LEFT = 0
    RIGHT = auto()
    UP = auto()
    DOWN = auto()


class GameStatus(Enum):
    RUN = auto()
    END = auto()
    WIN = auto()


class NextState:
    def __init__(self, score: int, grid: Grid):
        self.score = score
        self.grid = grid

    def log_merge(self, tile_value):
        self.score += 2 * tile_value


SPAWN_RATE_4 = 0.1
GRID_SIZE = 4
EMPTY_ROW = [0, 0, 0, 0]


class GameState:
    def __init__(self) -> None:
        """
        Create new GameState instance.
        """
        self.generator: Random = Random(time.time())
        self.grid: Grid = [[0 for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]
        self.reset()

    def reset(self) -> None:
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.grid[i][j] = 0
        self.score = 0
        self.status = GameStatus.RUN
        self.new_tiles(2)
        self.possible_moves: ActionMap = self.get_possible_moves()

    def set_grid(self, grid: Grid) -> None:
        """
        Set game grid.
        """
        if len(grid) != GRID_SIZE or len(grid[0]) != GRID_SIZE:
            raise ValueError("Grid must be 4x4.")
        self.grid = grid
        self.possible_moves = self.get_possible_moves()

    def new_tiles(self, count: int = 1) -> None:
        # Find empty squares
        free = []
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == 0:
                    free.append((i, j))

        for _ in range(count):
            # Choose empty square; Cache last move to check faster?
            fid = self.generator.randint(0, len(free) - 1)
            i, j = free.pop(fid)

            # 2 or 4 tile
            if self.generator.random() <= SPAWN_RATE_4:
                self.grid[i][j] = 4
            else:
                self.grid[i][j] = 2

    def get_possible_moves(self) -> ActionMap:
        action_map: ActionMap = {}

        # Fast check if no possible moves:
        possible = [False] * 4
        for i in range(GRID_SIZE):
            if all(possible):
                break
            for j in range(GRID_SIZE):
                if j and not (
                    possible[Action.LEFT.value] and possible[Action.RIGHT.value]
                ):
                    prev_c = self.grid[i][j - 1]
                    if self.grid[i][j] and prev_c == 0:
                        possible[Action.LEFT.value] = True
                    elif self.grid[i][j] and self.grid[i][j] == prev_c:
                        possible[Action.LEFT.value] = True
                        possible[Action.RIGHT.value] = True
                    elif self.grid[i][j] == 0 and prev_c:
                        possible[Action.RIGHT.value] = True
                if i and not (
                    possible[Action.UP.value] and possible[Action.DOWN.value]
                ):
                    prev_r = self.grid[i - 1]
                    if self.grid[i][j] and prev_r[j] == 0:
                        possible[Action.UP.value] = True
                    elif self.grid[i][j] and self.grid[i][j] == prev_r[j]:
                        possible[Action.UP.value] = True
                        possible[Action.DOWN.value] = True
                    elif self.grid[i][j] == 0 and prev_r[j]:
                        possible[Action.DOWN.value] = True

        if possible[Action.LEFT.value]:
            # Left
            state_left = NextState(self.score, [])
            for row in self.grid:
                r = []
                prev = 0
                for element in row:
                    if prev == 0:
                        prev = element
                    elif prev == element:
                        r.append(prev + element)
                        state_left.log_merge(prev)
                        prev = 0
                    elif element:
                        r.append(prev)
                        prev = element
                if prev:
                    if len(r) and prev == r[-1]:
                        r[-1] += prev
                        state_left.log_merge(prev)
                    else:
                        r.append(prev)
                state_left.grid.append(r + [0] * (GRID_SIZE - len(r)))
            action_map[Action.LEFT] = state_left

        if possible[Action.RIGHT.value]:
            # Right
            state_right = NextState(self.score, [])
            for row in self.grid:
                r = []
                prev = 0
                for element in reversed(row):
                    if element:
                        if prev == 0:
                            prev = element
                        elif prev == element:
                            r.append(prev + element)
                            state_right.log_merge(prev)
                            prev = 0
                        else:
                            r.append(prev)
                            prev = element
                if prev:
                    if len(r) and prev == r[-1]:
                        r[-1] += prev
                        state_right.log_merge(prev)
                    else:
                        r.append(prev)
                state_right.grid.append([0] * (GRID_SIZE - len(r)) + list(reversed(r)))
            action_map[Action.RIGHT] = state_right

        if possible[Action.UP.value]:
            # Up
            state_up = NextState(self.score, [])
            temp = [[], [], [], []]
            prev = [0, 0, 0, 0]
            for row in self.grid:
                for i in range(len(row)):
                    if prev[i] == 0:
                        prev[i] = row[i]
                    elif prev[i] == row[i]:
                        temp[i].append(prev[i] + row[i])
                        state_up.log_merge(prev[i])
                        prev[i] = 0
                    elif row[i]:
                        temp[i].append(prev[i])
                        prev[i] = row[i]
            for i in range(GRID_SIZE):
                if prev[i]:
                    temp[i].append(prev[i])
            # Take from stacks and add to map
            for i in range(GRID_SIZE):
                row = [0, 0, 0, 0]
                for j in range(GRID_SIZE):
                    if i < len(temp[j]):
                        row[j] = temp[j][i]
                state_up.grid.append(row)
            action_map[Action.UP] = state_up

        if possible[Action.DOWN.value]:
            # Down
            state_down = NextState(self.score, [])
            temp = [[], [], [], []]
            prev = [0, 0, 0, 0]
            for row in reversed(self.grid):
                for i in range(len(row)):
                    if prev[i] == 0:
                        prev[i] = row[i]
                    elif prev[i] == row[i]:
                        temp[i].append(prev[i] + row[i])
                        state_down.log_merge(prev[i])
                        prev[i] = 0
                    elif row[i]:
                        temp[i].append(prev[i])
                        prev[i] = row[i]
            for i in range(GRID_SIZE):
                if prev[i]:
                    temp[i].append(prev[i])
            for i in range(GRID_SIZE):
                row = [0, 0, 0, 0]
                for j in range(GRID_SIZE):
                    if GRID_SIZE - len(temp[j]) <= i:
                        row[j] = temp[j].pop()
                state_down.grid.append(row)
            action_map[Action.DOWN] = state_down

        return action_map

    def step(self, move: Action) -> GameStatus:
        # raise NotImplementedError("GameState.step not implemented.")
        next_state = self.possible_moves.get(move)
        if next_state:
            self.grid = next_state.grid
            self.score = next_state.score
            self.new_tiles()
            self.possible_moves = self.get_possible_moves()
            if len(self.possible_moves) == 0:
                self.status = GameStatus.END
        return self.status

    def print(self, fout: TextIO = sys.stdout) -> None:
        print(
            "In Progress" if self.status == GameStatus.RUN else "Game Over", file=fout
        )
        print(f"Score: {self.score}", file=fout)
        for row in self.grid:
            print(row, file=fout)
