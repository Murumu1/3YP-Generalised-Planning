import random

from util.constants import TILE_COUNT
from util.problem_generator import ProblemGenerator
from util.tile import Tile


class SnakeGenerator(ProblemGenerator):
    def __init__(self, problem_count: int, apple_count: int):
        super().__init__(problem_count)

        self._apple_count = apple_count

    def _generate_problem(self):
        board = [(x, y) for x in range(TILE_COUNT) for y in range(TILE_COUNT)]
        available_locations = board.copy()

        start_location = available_locations.pop(0)
        start = Tile(tile_location=start_location)
        goal_locations = random.sample(available_locations, self._apple_count)
        apples = []
        for g in goal_locations:
            apples.append(Tile(tile_location=g))