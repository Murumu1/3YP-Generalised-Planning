import sys

import pygame
from unified_planning.engines import CompilationKind
import unified_planning as up
from unified_planning.model import Object
from up_bfgp import BestFirstGeneralizedPlanner
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import Problem, OneshotPlanner
from util.constants import *
from util.tile import Tile
from dataclasses import dataclass


@dataclass
class Maze:
    tiles: list[Tile]
    start: Tile
    goal: Tile


# TODO: Fix issue when swapping tiles
class MazeProblemGenerator:

    def __init__(self, problem_count: int):
        self._reader = PDDLReader()

        self._mazes = []
        self._problems = []
        self._tile_object_mapping = {}

        for p in range(problem_count):
            curr_maze = self._generate_maze()
            self._mazes.append(curr_maze)
            self._problems.append(self._generate_problem(curr_maze))

    @staticmethod
    def _change_special_tile(screen: pygame.Surface, special_tile: Tile, conflict_tile: Tile, new_tile: Tile,
                             colour: tuple) -> tuple:

        # If the special tile is already on the maze
        if special_tile is not None:
            old_special_tile = special_tile.get_rect()
            pygame.draw.rect(screen, FILLED_TILE, old_special_tile)
            special_tile.set_position(tile=new_tile)
        else:
            special_tile = new_tile

        # If the new tile is the same as the conflict tile, override
        if conflict_tile is not None:
            if new_tile == conflict_tile:
                conflict_tile = None

        # Draw the new tile
        pygame.draw.rect(screen, colour, new_tile.get_rect())
        return special_tile, conflict_tile

    def _generate_maze(self) -> Maze:

        # Display set-up
        pygame.init()
        screen = pygame.display.set_mode(SCREEN_SIZE)
        clock = pygame.time.Clock()
        screen.fill(BACKGROUND)
        maze_generated = False

        # Maze set-up
        maze = []
        goal = None
        start = None
        to_change = START

        while not maze_generated:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    maze_generated = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        maze_generated = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    current_tile = Tile(pygame_position=pygame.mouse.get_pos())
                    if pygame.mouse.get_pressed()[0]:
                        if current_tile not in maze:
                            maze.append(current_tile)
                            pygame.draw.rect(screen, FILLED_TILE, current_tile.get_rect())
                        else:
                            maze.remove(current_tile)
                            if start is not None:
                                if current_tile == start:
                                    start = None
                            if goal is not None:
                                if current_tile == goal:
                                    goal = None
                            pygame.draw.rect(screen, BACKGROUND, current_tile.get_rect())
                    if pygame.mouse.get_pressed()[2]:
                        if current_tile in maze:
                            if to_change == START:
                                start, goal = self._change_special_tile(screen, start, goal, current_tile, START_TILE)
                                to_change = GOAL
                            elif to_change == GOAL:
                                goal, start = self._change_special_tile(screen, goal, start, current_tile, GOAL_TILE)
                                to_change = START

            pygame.display.flip()
            clock.tick(60)

        # Ensure start and goal has been set
        if start is None or goal is None:
            raise Exception("You must set a start [red] and a goal [green] by left clicking tiles.")

        print("[DEBUG] Maze generated successfully")
        pygame.quit()
        return Maze(maze, start, goal)

    def _add_mapping(self, tile: Tile, *pddl_objects: Object) -> None:
        tile_hash = hash(tile)
        pddl_objects = list(pddl_objects)
        observed_mapping = self._tile_object_mapping.get(tile_hash)
        if observed_mapping:
            self._tile_object_mapping[tile_hash].extend(pddl_objects)
        else:
            self._tile_object_mapping[tile_hash] = pddl_objects

    def _get_mapping(self, tile: Tile) -> list[Object]:
        tile_hash = hash(tile)
        return self._tile_object_mapping[tile_hash] if self._tile_object_mapping.get(tile_hash) else []

    def _generate_problem(self, maze: Maze) -> Problem:
        raise NotImplementedError

    def display_problems(self) -> None:
        """
        Display problems for debugging purposes
        """
        for i, problem in enumerate(self._problems):
            print(f"Problem {i}:")
            print(problem, "\n")

    def solve_each(self) -> None:
        """
        Solves each problem one by one using classical planning
        """
        for i, problem in enumerate(self._problems):
            print(f"Plan {i + 1}:")
            with OneshotPlanner(problem_kind=problem.kind) as planner:
                result = planner.solve(problem)
                if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
                    print(f"Found plan with {len(result.plan.actions)} steps!")
                    for i, action in enumerate(result.plan.actions):
                        print(f"{i}: {action}")
                else:
                    print("Unable to find a plan.")
            print("")

    # TODO: Ensure planner acts correctly (shows messages and outputs to chosen folder)
    def solve_all(self, program_lines: int = 15) -> None:
        """
        Solves all problems at once using generalised planning
        :param program_lines: constraint on the maximum number of lines available to the planner
        """
        with BestFirstGeneralizedPlanner(program_lines=program_lines) as planner:
            planner.solve(self._problems, output_stream=sys.stdout)
