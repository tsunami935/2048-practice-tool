from __future__ import annotations
import unittest
from collections import defaultdict
from io import StringIO

from gamestate import GameState, GameStatus, Grid, Action

EMPTY_ROW = [0, 0, 0, 0]


def count_blocks(grid: Grid) -> dict[int, int]:
    count = defaultdict(int)
    for row in grid:
        for element in row:
            if element:
                count[element] += 1
    return count


def total_blocks(grid: Grid) -> int:
    return sum(count_blocks(grid).values())


# def is_equal_states(grid1: Grid, grid2: Grid) -> bool:
#     assert len(grid1) == len(grid2)
#     assert len(grid1[0]) == len(grid2[0])
#     for i in range(len(grid1)):
#         for j in range(len(grid1[0])):
#             if grid1[i][j] != grid2[i][j]:
#                 return False
#     return True


class TestGameState(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()

    def test_init(self):
        num_blocks = total_blocks(self.game_state.grid)

        self.assertEqual(0, self.game_state.score)
        self.assertEqual(4, len(self.game_state.grid))
        self.assertEqual(4, len(self.game_state.grid[0]))
        self.assertEqual(2, num_blocks)

    def test_reset(self):
        self.game_state.reset()

        num_blocks = total_blocks(self.game_state.grid)

        self.assertEqual(0, self.game_state.score)
        self.assertEqual(GameStatus.RUN, self.game_state.status)
        self.assertEqual(2, num_blocks)

    def test_set_grid(self):
        grid: Grid = [EMPTY_ROW, [2, 0, 0, 0], [0, 2, 0, 0], EMPTY_ROW]
        self.game_state.set_grid(grid)
        self.assertEqual(grid, self.game_state.grid)

    def test_new_tiles(self):
        num_blocks = total_blocks(self.game_state.grid)
        self.assertEqual(2, num_blocks)

        self.game_state.new_tiles()
        num_blocks = total_blocks(self.game_state.grid)
        self.assertEqual(3, num_blocks)

        self.game_state.new_tiles(3)
        num_blocks = total_blocks(self.game_state.grid)
        self.assertEqual(6, num_blocks)

        while num_blocks < 16:
            with self.subTest(num_blocks=num_blocks):
                self.game_state.new_tiles(2)
                new_blocks = total_blocks(self.game_state.grid)
                self.assertEqual(num_blocks + 2, new_blocks)
                num_blocks = new_blocks

        count = count_blocks(self.game_state.grid)
        self.assertEqual(16, count.get(2, 0) + count.get(4, 0))
        self.assertRaises(Exception, self.game_state.new_tiles)

    def test_get_possible_moves_move_only(self):
        grid1: Grid = [EMPTY_ROW, [2, 0, 0, 0], [0, 2, 0, 0], EMPTY_ROW]
        result: dict[Action, Grid] = {
            Action.LEFT: [EMPTY_ROW, [2, 0, 0, 0], [2, 0, 0, 0], EMPTY_ROW],
            Action.RIGHT: [EMPTY_ROW, [0, 0, 0, 2], [0, 0, 0, 2], EMPTY_ROW],
            Action.DOWN: [EMPTY_ROW, EMPTY_ROW, EMPTY_ROW, [2, 2, 0, 0]],
            Action.UP: [[2, 2, 0, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW],
        }

        self.game_state.grid = grid1
        possible_moves = self.game_state.get_possible_moves()
        for action in result.keys():
            with self.subTest(action=action):
                self.assertEqual(2, total_blocks(possible_moves[action].grid))
                self.assertEqual(result[action], possible_moves[action].grid)
                self.assertEqual(0, possible_moves[action].score)

    def test_get_possible_moves_single_merge_adjacent(self):
        grid_horizontal: Grid = [[2, 2, 0, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_left: Grid = [[4, 0, 0, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_right: Grid = [[0, 0, 0, 4], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]

        self.game_state.grid = grid_horizontal
        possible_moves = self.game_state.get_possible_moves()
        self.assertEqual(possible_moves[Action.LEFT].grid, result_left)
        self.assertEqual(possible_moves[Action.RIGHT].grid, result_right)
        self.assertEqual(4, possible_moves[Action.LEFT].score)
        self.assertEqual(4, possible_moves[Action.RIGHT].score)

        grid_vertical: Grid = [[0, 2, 0, 0], [0, 2, 0, 0], EMPTY_ROW, EMPTY_ROW]
        result_up: Grid = [[0, 4, 0, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_down: Grid = [EMPTY_ROW, EMPTY_ROW, EMPTY_ROW, [0, 4, 0, 0]]

        self.game_state.grid = grid_vertical
        possible_moves = self.game_state.get_possible_moves()
        self.assertEqual(possible_moves[Action.UP].grid, result_up)
        self.assertEqual(possible_moves[Action.DOWN].grid, result_down)
        self.assertEqual(4, possible_moves[Action.UP].score)
        self.assertEqual(4, possible_moves[Action.DOWN].score)

    def test_get_possible_moves_single_merge_space(self):
        grid_horizontal: Grid = [[2, 0, 2, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_left: Grid = [[4, 0, 0, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_right: Grid = [[0, 0, 0, 4], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]

        self.game_state.grid = grid_horizontal
        possible_moves = self.game_state.get_possible_moves()
        self.assertEqual(possible_moves[Action.LEFT].grid, result_left)
        self.assertEqual(possible_moves[Action.RIGHT].grid, result_right)
        self.assertEqual(4, possible_moves[Action.LEFT].score)
        self.assertEqual(4, possible_moves[Action.RIGHT].score)

        grid_vertical: Grid = [[0, 2, 0, 0], EMPTY_ROW, [0, 2, 0, 0], EMPTY_ROW]
        result_up: Grid = [[0, 4, 0, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_down: Grid = [EMPTY_ROW, EMPTY_ROW, EMPTY_ROW, [0, 4, 0, 0]]

        self.game_state.grid = grid_vertical
        possible_moves = self.game_state.get_possible_moves()
        self.assertEqual(possible_moves[Action.UP].grid, result_up)
        self.assertEqual(possible_moves[Action.DOWN].grid, result_down)
        self.assertEqual(4, possible_moves[Action.UP].score)
        self.assertEqual(4, possible_moves[Action.DOWN].score)

    def test_get_possible_moves_single_merge_three_in_a_row(self):
        grid_horizontal: Grid = [[2, 2, 2, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_left: Grid = [[4, 2, 0, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_right: Grid = [[0, 0, 2, 4], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]

        self.game_state.grid = grid_horizontal
        possible_moves = self.game_state.get_possible_moves()
        self.assertEqual(possible_moves[Action.LEFT].grid, result_left)
        self.assertEqual(possible_moves[Action.RIGHT].grid, result_right)
        self.assertEqual(4, possible_moves[Action.LEFT].score)
        self.assertEqual(4, possible_moves[Action.RIGHT].score)

        grid_vertical: Grid = [[0, 2, 0, 0], [0, 2, 0, 0], [0, 2, 0, 0], EMPTY_ROW]
        result_up: Grid = [[0, 4, 0, 0], [0, 2, 0, 0], EMPTY_ROW, EMPTY_ROW]
        result_down: Grid = [EMPTY_ROW, EMPTY_ROW, [0, 2, 0, 0], [0, 4, 0, 0]]

        self.game_state.grid = grid_vertical
        possible_moves = self.game_state.get_possible_moves()
        self.assertEqual(possible_moves[Action.UP].grid, result_up)
        self.assertEqual(possible_moves[Action.DOWN].grid, result_down)
        self.assertEqual(4, possible_moves[Action.UP].score)
        self.assertEqual(4, possible_moves[Action.DOWN].score)

    def test_get_possible_moves_double_merge_different(self):
        grid_horizontal: Grid = [[2, 2, 4, 4], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_left: Grid = [[4, 8, 0, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_right: Grid = [[0, 0, 4, 8], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]

        self.game_state.grid = grid_horizontal
        possible_moves = self.game_state.get_possible_moves()
        self.assertEqual(possible_moves[Action.LEFT].grid, result_left)
        self.assertEqual(possible_moves[Action.RIGHT].grid, result_right)
        self.assertEqual(12, possible_moves[Action.LEFT].score)
        self.assertEqual(12, possible_moves[Action.RIGHT].score)

        grid_vertical: Grid = [[0, 2, 0, 0], [0, 2, 0, 0], [0, 4, 0, 0], [0, 4, 0, 0]]
        result_up: Grid = [[0, 4, 0, 0], [0, 8, 0, 0], EMPTY_ROW, EMPTY_ROW]
        result_down: Grid = [EMPTY_ROW, EMPTY_ROW, [0, 4, 0, 0], [0, 8, 0, 0]]

        self.game_state.grid = grid_vertical
        possible_moves = self.game_state.get_possible_moves()
        self.assertEqual(possible_moves[Action.UP].grid, result_up)
        self.assertEqual(possible_moves[Action.DOWN].grid, result_down)
        self.assertEqual(12, possible_moves[Action.UP].score)
        self.assertEqual(12, possible_moves[Action.DOWN].score)

    def test_get_possible_moves_double_merge_same(self):
        grid_horizontal: Grid = [[2, 2, 2, 2], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_left: Grid = [[4, 4, 0, 0], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        result_right: Grid = [[0, 0, 4, 4], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]

        self.game_state.grid = grid_horizontal
        possible_moves = self.game_state.get_possible_moves()
        self.assertEqual(possible_moves[Action.LEFT].grid, result_left)
        self.assertEqual(possible_moves[Action.RIGHT].grid, result_right)
        self.assertEqual(8, possible_moves[Action.LEFT].score)
        self.assertEqual(8, possible_moves[Action.RIGHT].score)

        grid_vertical: Grid = [[0, 2, 0, 0], [0, 2, 0, 0], [0, 2, 0, 0], [0, 2, 0, 0]]
        result_up: Grid = [[0, 4, 0, 0], [0, 4, 0, 0], EMPTY_ROW, EMPTY_ROW]
        result_down: Grid = [EMPTY_ROW, EMPTY_ROW, [0, 4, 0, 0], [0, 4, 0, 0]]

        self.game_state.grid = grid_vertical
        possible_moves = self.game_state.get_possible_moves()
        self.assertEqual(possible_moves[Action.UP].grid, result_up)
        self.assertEqual(possible_moves[Action.DOWN].grid, result_down)
        self.assertEqual(8, possible_moves[Action.UP].score)
        self.assertEqual(8, possible_moves[Action.DOWN].score)

    def test_step_move_available(self):
        grid: Grid = [[2, 2, 0, 0], [0, 0, 0, 2], EMPTY_ROW, EMPTY_ROW]

        # result_left: Grid = [[4, 0, 0, 0], [2, 0, 0, 0], EMPTY_ROW, EMPTY_ROW]
        self.game_state.set_grid(grid)
        self.assertEqual(GameStatus.RUN, self.game_state.step(Action.LEFT))
        self.assertEqual(3, total_blocks(self.game_state.grid))
        self.assertEqual(4, self.game_state.grid[0][0])
        self.assertEqual(2, self.game_state.grid[1][0])
        self.assertEqual(4, self.game_state.score)

        # result_right: Grid = [[0, 0, 0, 4], [0, 0, 0, 2], EMPTY_ROW, EMPTY_ROW]
        self.game_state.reset()
        self.game_state.set_grid(grid)
        self.assertEqual(GameStatus.RUN, self.game_state.step(Action.RIGHT))
        self.assertEqual(3, total_blocks(self.game_state.grid))
        self.assertEqual(4, self.game_state.grid[0][3])
        self.assertEqual(2, self.game_state.grid[1][3])
        self.assertEqual(4, self.game_state.score)

        # result_up: Grid = [[2, 2, 0, 2], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        self.game_state.reset()
        self.game_state.set_grid(grid)
        self.assertEqual(GameStatus.RUN, self.game_state.step(Action.UP))
        self.assertEqual(4, total_blocks(self.game_state.grid))
        self.assertEqual(2, self.game_state.grid[0][0])
        self.assertEqual(2, self.game_state.grid[0][1])
        self.assertEqual(2, self.game_state.grid[0][3])
        self.assertEqual(0, self.game_state.score)

        # result_down: Grid = [EMPTY_ROW, EMPTY_ROW, EMPTY_ROW, [2, 2, 0, 2]]
        self.game_state.reset()
        self.game_state.set_grid(grid)
        self.assertEqual(GameStatus.RUN, self.game_state.step(Action.DOWN))
        self.assertEqual(4, total_blocks(self.game_state.grid))
        self.assertEqual(2, self.game_state.grid[3][0])
        self.assertEqual(2, self.game_state.grid[3][1])
        self.assertEqual(2, self.game_state.grid[3][3])
        self.assertEqual(0, self.game_state.score)

    def test_step_game_end(self):
        grid: Grid = [[2, 4, 16, 64], [4, 2, 32, 32], [2, 4, 16, 64], [8, 2, 4, 8]]
        self.game_state.set_grid(grid)
        self.assertEqual(GameStatus.END, self.game_state.step(Action.LEFT))

    def test_step_invalid_move(self):
        # Test that invalid move makes no changes to game state

        grid_left: Grid = [[2, 0, 0, 0], [2, 0, 0, 0], EMPTY_ROW, EMPTY_ROW]
        self.game_state.set_grid(grid_left)
        self.assertEqual(GameStatus.RUN, self.game_state.step(Action.LEFT))
        self.assertEqual(grid_left, self.game_state.grid)
        self.assertEqual(0, self.game_state.score)

        grid_right: Grid = [[0, 0, 0, 2], [0, 0, 0, 2], EMPTY_ROW, EMPTY_ROW]
        self.game_state.set_grid(grid_right)
        self.assertEqual(GameStatus.RUN, self.game_state.step(Action.RIGHT))
        self.assertEqual(grid_right, self.game_state.grid)
        self.assertEqual(0, self.game_state.score)

        grid_up: Grid = [[2, 2, 0, 2], EMPTY_ROW, EMPTY_ROW, EMPTY_ROW]
        self.game_state.set_grid(grid_up)
        self.assertEqual(GameStatus.RUN, self.game_state.step(Action.UP))
        self.assertEqual(grid_up, self.game_state.grid)
        self.assertEqual(0, self.game_state.score)

        grid_down: Grid = [EMPTY_ROW, EMPTY_ROW, EMPTY_ROW, [2, 2, 0, 2]]
        self.game_state.set_grid(grid_down)
        self.assertEqual(GameStatus.RUN, self.game_state.step(Action.DOWN))
        self.assertEqual(grid_down, self.game_state.grid)
        self.assertEqual(0, self.game_state.score)

    def test_print_run(self):
        buffer = StringIO()
        grid: Grid = [[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, 2, 0], [0, 0, 0, 2]]

        self.game_state.set_grid(grid)
        self.game_state.score = 24

        self.game_state.print(buffer)
        buffer.seek(0)
        self.assertEqual("In Progress\n", buffer.readline())
        self.assertEqual("Score: 24\n", buffer.readline())
        self.assertEqual("[2, 0, 0, 0]\n", buffer.readline())
        self.assertEqual("[0, 2, 0, 0]\n", buffer.readline())
        self.assertEqual("[0, 0, 2, 0]\n", buffer.readline())
        self.assertEqual("[0, 0, 0, 2]\n", buffer.readline())

    def test_print_end(self):
        buffer = StringIO()
        grid: Grid = [[2, 4, 16, 64], [4, 2, 32, 32], [2, 4, 16, 64], [8, 2, 4, 8]]

        self.game_state.set_grid(grid)
        self.game_state.step(Action.LEFT)

        self.game_state.print(buffer)
        buffer.seek(0)
        self.assertEqual("Game Over\n", buffer.readline())
        self.assertEqual("Score: 64\n", buffer.readline())
        self.assertEqual("[2, 4, 16, 64]\n", buffer.readline())
        self.assertTrue(buffer.readline().startswith("[4, 2, 64, "))
        self.assertEqual("[2, 4, 16, 64]\n", buffer.readline())
        self.assertEqual("[8, 2, 4, 8]\n", buffer.readline())

if __name__ == "__main__":
    unittest.main()
