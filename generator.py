import pygame
from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.shortcuts import Object, Problem
from constants import *
from tile import Tile


class MazeProblemGenerator:

    def __init__(self, domain_file_path: str):

        self.domain_file_path = domain_file_path
        self._problem = None

    @staticmethod
    def _change_special_tile(screen: pygame.Surface, special_tile: Tile, conflict_tile: Tile, new_tile: Tile,
                             colour: tuple) -> tuple:
        """
        Logic for setting the special tiles.
        Special tile is either start/goal and conflict tile is either goal/start respectively.
        """

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

    def generate_problem(self, problem_name: str) -> Problem:
        """
        Generates a problem in UP, by providing an interface for creating a maze.

        * To create a maze, left-click on any part of the screen to mark it as a path, and left-click again to remove it.
        * Right-click a tile on the maze to set it as a start or goal.
        * Exit the program to generate the problem.

        :param problem_name: Name of the problem to generate.
        """

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

                # Exit when pygame window has been closed
                if event.type == pygame.QUIT:
                    maze_generated = True

                if event.type == pygame.MOUSEBUTTONDOWN:

                    # Obtain tile at mouse position after click
                    current_tile = Tile(pygame_position=pygame.mouse.get_pos())

                    # Left-click event
                    if pygame.mouse.get_pressed()[0]:

                        # Add tile to maze if tile not in maze
                        if current_tile not in maze:
                            maze.append(current_tile)
                            pygame.draw.rect(screen, FILLED_TILE, current_tile.get_rect())

                        # Remove it otherwise
                        else:
                            maze.remove(current_tile)
                            if start is not None:
                                if current_tile == start:
                                    start = None
                            if goal is not None:
                                if current_tile == goal:
                                    goal = None
                            pygame.draw.rect(screen, BACKGROUND, current_tile.get_rect())

                    # Right-click event
                    if pygame.mouse.get_pressed()[2]:
                        if current_tile in maze:
                            if to_change == START:
                                start, goal = self._change_special_tile(
                                    screen, start, goal, current_tile, START_TILE
                                )
                                to_change = GOAL
                            elif to_change == GOAL:
                                goal, start = self._change_special_tile(
                                    screen, goal, start, current_tile, GOAL_TILE
                                )
                                to_change = START

            pygame.display.flip()
            clock.tick(60)

        # Ensure start and goal has been set
        if start is None or goal is None:
            raise Exception("You must set a start [red] and a goal [green] by left clicking tiles.")

        # Problem set-up
        reader = PDDLReader()
        self._problem = reader.parse_problem(self.domain_file_path)
        self._problem.name = problem_name

        # Create objects
        x_objects = [Object(f"x{i}", self._problem.user_type(POSITION)) for i in range(TILE_COUNT)]
        y_objects = [Object(f"y{i}", self._problem.user_type(POSITION)) for i in range(TILE_COUNT)]
        direction_objects = [Object(direction, self._problem.user_type("direction")) for direction in DIRECTIONS]
        self._problem.add_objects(x_objects + y_objects + direction_objects)

        # Set initial value for fluents
        # inc(?a ?b) from x0->x9, y0->y9 := true
        for i in range(1, TILE_COUNT):
            self._problem.set_initial_value(
                self._problem.fluent(INC)(x_objects[i - 1], x_objects[i]),
                True
            )
            self._problem.set_initial_value(
                self._problem.fluent(INC)(y_objects[i - 1], y_objects[i]),
                True
            )

        # dec(?a ?b) from x9->x0 y9->y0 := true
        for i in range(1, TILE_COUNT):
            self._problem.set_initial_value(
                self._problem.fluent(DEC)(x_objects[i], x_objects[i - 1]),
                True
            )
            self._problem.set_initial_value(
                self._problem.fluent(DEC)(y_objects[i], y_objects[i - 1]),
                True
            )

        # path(?x ?y) for all tiles in maze := true
        for tile in maze:
            x, y = tile.get_position()
            self._problem.set_initial_value(
                self._problem.fluent(PATH)(x_objects[x], y_objects[y]),
                True
            )

        # is-{d}(?d) for all directions := true
        for i in range(len(DIRECTIONS)):
            self._problem.set_initial_value(
                self._problem.fluent(DIRECTION_CONDITIONS[i])(direction_objects[i]),
                True
            )

        # right-rot(?d ?dn) for all directions, where dn is the direction to the right := true
        for i in range(len(DIRECTIONS)):
            self._problem.set_initial_value(
                self._problem.fluent(RIGHT_ROT)(
                    direction_objects[i],
                    direction_objects[i + 1 if i + 1 < len(DIRECTIONS) else 0]
                ),
                True
            )

        # left-rot(?d ?dn) for all directions, where dn is the direction to the left := true
        for i in range(len(DIRECTIONS)):
            self._problem.set_initial_value(
                self._problem.fluent(LEFT_ROT)(
                    direction_objects[i],
                    direction_objects[i - 1 if i - 1 >= 0 else len(DIRECTIONS) - 1]
                ),
                True
            )

        # facing(?d) ?d = north := true
        self._problem.set_initial_value(
            self._problem.fluent(FACING)(direction_objects[0]),
            True
        )

        # Start position
        s_x, s_y = start.get_position()

        # at(?x ?y) ?x = s_x, ?y = s_y := true
        self._problem.set_initial_value(
            self._problem.fluent(AT)(x_objects[s_x], y_objects[s_y]),
            True
        )

        # Goal position
        g_x, g_y = goal.get_position()

        # Goal state: at(g_x g_y)
        self._problem.add_goal(
            self._problem.fluent(AT)(x_objects[g_x], y_objects[g_y])
        )

        return self._problem

    def export(self, directory: str) -> None:
        """
        Exports the problem saved in current object to a PDDL file.
        :param directory: The directory of the PDDL file.
        """
        writer = PDDLWriter(self._problem)
        writer.write_problem(f"{directory}/{self._problem.name}.pddl")
