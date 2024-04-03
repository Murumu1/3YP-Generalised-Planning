import random
import pygame.display
from unified_planning.model import Object
from unified_planning.shortcuts import Not
from util.constants import *
from util.environments import SnakeEnvironment, Environment
from util.problem_generator import ProblemGenerator
from util.tile import Tile, TileCollection


class SnakeGenerator(ProblemGenerator):
    def __init__(self, **options):
        self._apple_count = options.get("apple_count", 5)
        super().__init__("snake", **options)

    def _generate_environment_auto(self) -> Environment:
        board = TileCollection([Tile(tile_position=(x, y)) for x in range(TILE_COUNT) for y in range(TILE_COUNT)])
        available_locations = board.copy()

        start = available_locations.pop(random.randint(0, len(available_locations) - 1))
        goals = random.sample(available_locations, self._apple_count)
        apples = TileCollection()
        for goal in goals:
            apples.append(goal)

        screen = pygame.display.set_mode(SCREEN_SIZE)
        screen.fill(BACKGROUND)
        for tile in board:
            pygame.draw.rect(screen, FILLED_TILE, tile.get_rect())
            pygame.display.flip()

        current_colour = INITIAL_APPLE
        for apple in apples:
            pygame.draw.rect(screen, current_colour, apple.get_rect())
            pygame.display.flip()
            current_colour = self._darken_colour(current_colour)

        pygame.draw.rect(screen, START_TILE, start.get_rect())
        pygame.display.flip()

        self._save_pygame_environment(screen)
        pygame.quit()

        return SnakeEnvironment(board, start, apples)

    def _generate_environment_manual(self) -> Environment:
        pass

    def _setup_problem(self, environment: SnakeEnvironment) -> None:

        for tile in environment.board:
            position = tile.get_position()
            tile_obj = Object(f"p{position[0]}-{position[1]}", self._problem.user_type(POSITION))
            self._add_mapping(tile, tile_obj)
            self._problem.add_object(tile_obj)

        dummy_apple = Object(DUMMYPOINT, self._problem.user_type(POSITION))

        for tile in environment.board:
            for neighbour in environment.board.find_neighbours(tile):
                neighbour_object = self._get_mapping(neighbour)
                current_object = self._get_mapping(tile)
                self._problem.set_initial_value(self._problem.fluent(PATH)(neighbour_object, current_object), True)
                self._problem.set_initial_value(self._problem.fluent(PATH)(current_object, neighbour_object), True)

        start_object = self._get_mapping(environment.start)

        tail_tile = environment.board.find_neighbours(environment.start)[0]
        tail_object = self._get_mapping(tail_tile)

        self._problem.set_initial_value(self._problem.fluent(HEAD_AT)(start_object), True)
        self._problem.set_initial_value(self._problem.fluent(TAIL_AT)(tail_object), True)
        self._problem.set_initial_value(self._problem.fluent(BODY_CON)(start_object, tail_object), True)
        self._problem.set_initial_value(self._problem.fluent(BLOCKED)(start_object), True)
        self._problem.set_initial_value(self._problem.fluent(BLOCKED)(tail_object), True)
        self._problem.set_initial_value(self._problem.fluent(APPLE_AT)(self._get_mapping(environment.apples[0])), True)
        self._problem.set_initial_value(self._problem.fluent(SPAWN_APPLE)(self._get_mapping(environment.apples[1])), True)

        for i in range(1, len(environment.apples)):
            apple_obj = self._get_mapping(environment.apples[i])
            if i + 1 < len(environment.apples):
                next_apple_obj = self._get_mapping(environment.apples[i + 1])
            else:
                next_apple_obj = dummy_apple
            self._problem.set_initial_value(self._problem.fluent(NEXT_APPLE)(apple_obj, next_apple_obj), True)

        for i in range(len(environment.apples)):
            self._problem.add_goal(Not(self._problem.fluent(APPLE_AT)(self._get_mapping(environment.apples[i]))))

    @staticmethod
    def _darken_colour(colour):
        return round(colour[0] * 0.95), round(colour[1] * 0.95), round(colour[2] * 0.95)

