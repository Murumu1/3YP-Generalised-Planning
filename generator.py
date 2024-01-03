import pygame
from glob import glob
from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.shortcuts import Object, Problem


class MazeProblemGenerator:

    def __init__(self, domain_file_path: str):

        # Colours
        self.BACKGROUND = (255, 255, 255)
        self.FILLED_TILE = (255, 255, 0)
        self.GOAL_TILE = (0, 255, 0)
        self.START_TILE = (255, 0, 0)

        # Constants
        self.SCREEN_SIZE = self.WIDTH, self.HEIGHT = 500, 500
        self.TILE_COUNT = 10
        self.TILE_SIZE = self.TILE_WIDTH, self.TILE_HEIGHT = (
            self.WIDTH // self.TILE_COUNT,
            self.HEIGHT // self.TILE_COUNT
        )

        self.domain_file_path = domain_file_path
        self._problem = None
        self._reset_tiles()

        self._screen = None
        self._clock = None

    def _reset_tiles(self) -> None:
        self._maze = []
        self._goal = None
        self._start = None
        self._to_change = 'start'

    def _main_loop(self) -> None:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN:

                current_tile = self._get_tile_position(pygame.mouse.get_pos())
                current_tile_rect = self._get_tile_rect(current_tile)

                if pygame.mouse.get_pressed()[0]:
                    if current_tile not in self._maze:
                        self._maze.append(current_tile)
                        pygame.draw.rect(self._screen, self.FILLED_TILE, current_tile_rect)
                    else:
                        self._maze.remove(current_tile)
                        if current_tile == self._start:
                            self._start = None
                        if current_tile == self._goal:
                            self._goal = None
                        pygame.draw.rect(self._screen, self.BACKGROUND, current_tile_rect)

                if pygame.mouse.get_pressed()[2]:
                    if current_tile in self._maze:

                        if self._to_change == 'start':
                            self._start, self._goal = self._change_special_tile(
                                self._start, self._goal, current_tile, current_tile_rect, self.START_TILE
                            )
                            self._to_change = 'goal'

                        elif self._to_change == 'goal':
                            self._start, self._goal = self._change_special_tile(
                                self._goal, self._start, current_tile, current_tile_rect, self.GOAL_TILE
                            )
                            self._to_change = 'start'

        pygame.display.flip()
        self._clock.tick(60)
        self._main_loop()

    def _change_special_tile(self, special_tile: tuple, conflict_tile: tuple, new_tile: tuple, new_tile_rect: pygame.Rect, colour: tuple) -> tuple:
        if special_tile:
            old_special_tile = self._get_tile_rect(special_tile)
            pygame.draw.rect(self._screen, self.FILLED_TILE, old_special_tile)
        special_tile = new_tile
        if new_tile == conflict_tile:
            conflict_tile = None
        pygame.draw.rect(self._screen, colour, new_tile_rect)
        return (
            special_tile,
            conflict_tile
        )

    def _get_tile_position(self, position: tuple) -> tuple:
        return (
            position[0] // self.TILE_WIDTH,
            position[1] // self.TILE_HEIGHT
        )

    def _get_tile_rect(self, tile_position: tuple) -> pygame.Rect:
        return pygame.Rect(
            tile_position[0] * self.TILE_WIDTH,
            tile_position[1] * self.TILE_HEIGHT,
            self.TILE_WIDTH,
            self.TILE_HEIGHT
        )

    def generate_problem(self, problem_name: str) -> Problem:

        self._reset_tiles()

        pygame.init()
        self._screen = pygame.display.set_mode(self.SCREEN_SIZE)
        self._clock = pygame.time.Clock()
        self._screen.fill(self.BACKGROUND)
        self._main_loop()

        reader = PDDLReader()
        self._problem = reader.parse_problem(self.domain_file_path)
        self._problem.name = problem_name

        directions = ["north", "east", "south", "west"]
        x_objects = [Object(f"x{i}", self._problem.user_type("position")) for i in range(self.TILE_COUNT)]
        y_objects = [Object(f"y{i}", self._problem.user_type("position")) for i in range(self.TILE_COUNT)]
        direction_objects = [Object(direction, self._problem.user_type("direction")) for direction in directions]
        self._problem.add_objects(x_objects + y_objects + direction_objects)

        for i in range(1, self.TILE_COUNT):
            self._problem.set_initial_value(
                self._problem.fluent("inc")(x_objects[i - 1], x_objects[i]),
                True
            )
            self._problem.set_initial_value(
                self._problem.fluent("inc")(y_objects[i - 1], y_objects[i]),
                True
            )

        for i in range(1, self.TILE_COUNT):
            self._problem.set_initial_value(
                self._problem.fluent("dec")(x_objects[i], x_objects[i - 1]),
                True
            )
            self._problem.set_initial_value(
                self._problem.fluent("dec")(y_objects[i], y_objects[i - 1]),
                True
            )

        for tile in self._maze:
            self._problem.set_initial_value(
                self._problem.fluent("path")(x_objects[tile[0]], y_objects[tile[1]]),
                True
            )

        for i in range(len(directions)):
            self._problem.set_initial_value(
                self._problem.fluent(f"is-{directions[i]}")(direction_objects[i]),
                True
            )

        for i in range(len(directions)):
            self._problem.set_initial_value(
                self._problem.fluent("right-rot")(
                    direction_objects[i],
                    direction_objects[i + 1 if i + 1 < len(directions) else 0]
                ),
                True
            )

        for i in range(len(directions)):
            self._problem.set_initial_value(
                self._problem.fluent("left-rot")(
                    direction_objects[i],
                    direction_objects[i - 1 if i - 1 >= 0 else len(directions) - 1]
                ),
                True
            )

        self._problem.set_initial_value(
            self._problem.fluent("facing")(direction_objects[0]),
            True
        )

        self._problem.set_initial_value(
            self._problem.fluent("at")(x_objects[self._start[0]], y_objects[self._start[1]]),
            True
        )

        self._problem.add_goal(
            self._problem.fluent("at")(x_objects[self._goal[0]], y_objects[self._goal[1]])
        )

        return self._problem

    def export(self, directory: str) -> None:
        writer = PDDLWriter(self._problem)
        writer.write_problem(f"{directory}/{self._problem.name}.pddl")
