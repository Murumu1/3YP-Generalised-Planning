import pygame
from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.shortcuts import Object, Problem
from constants import *
from tile import Tile


class MazeProblemGenerator:

    def __init__(self):

        self._pointer = 0
        self._maze = []
        self._goal = None
        self._start = None

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

    def generate_maze(self) -> None:
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
        self._maze = []
        self._goal = None
        self._start = None
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
                        if current_tile not in self._maze:
                            self._maze.append(current_tile)
                            pygame.draw.rect(screen, FILLED_TILE, current_tile.get_rect())

                        # Remove it otherwise
                        else:
                            self._maze.remove(current_tile)
                            if self._start is not None:
                                if current_tile == self._start:
                                    self._start = None
                            if self._goal is not None:
                                if current_tile == self._goal:
                                    self._goal = None
                            pygame.draw.rect(screen, BACKGROUND, current_tile.get_rect())

                    # Right-click event
                    if pygame.mouse.get_pressed()[2]:
                        if current_tile in self._maze:
                            if to_change == START:
                                self._start, self._goal = self._change_special_tile(
                                    screen, self._start, self._goal, current_tile, START_TILE
                                )
                                to_change = GOAL
                            elif to_change == GOAL:
                                self._goal, self._start = self._change_special_tile(
                                    screen, self._goal, self._start, current_tile, GOAL_TILE
                                )
                                to_change = START

            pygame.display.flip()
            clock.tick(60)

        # Ensure start and goal has been set
        if self._start is None or self._goal is None:
            raise Exception("You must set a start [red] and a goal [green] by left clicking tiles.")

        print("Maze generated successfully")

    def generate_problem(self, domain, problem_name: str):

        # Problem set-up
        reader = PDDLReader()
        problem = reader.parse_problem(domain)
        problem.name = problem_name

        # Create objects
        x_objects = [Object(f"x{i}", problem.user_type(POSITION)) for i in range(TILE_COUNT)]
        y_objects = [Object(f"y{i}", problem.user_type(POSITION)) for i in range(TILE_COUNT)]
        direction_objects = [Object(direction, problem.user_type("direction")) for direction in DIRECTIONS]
        problem.add_objects(x_objects + y_objects + direction_objects)

        # Set initial value for fluents
        # inc(?a ?b) from x0->x9, y0->y9 := true
        for i in range(1, TILE_COUNT):
            problem.set_initial_value(
                problem.fluent(INC)(x_objects[i - 1], x_objects[i]),
                True
            )
            problem.set_initial_value(
                problem.fluent(INC)(y_objects[i - 1], y_objects[i]),
                True
            )

        # dec(?a ?b) from x9->x0 y9->y0 := true
        for i in range(1, TILE_COUNT):
            problem.set_initial_value(
                problem.fluent(DEC)(x_objects[i], x_objects[i - 1]),
                True
            )
            problem.set_initial_value(
                problem.fluent(DEC)(y_objects[i], y_objects[i - 1]),
                True
            )

        # path(?x ?y) for all tiles in maze := true
        for tile in self._maze:
            x, y = tile.get_position()
            problem.set_initial_value(
                problem.fluent(PATH)(x_objects[x], y_objects[y]),
                True
            )

        # is-{d}(?d) for all directions := true
        for i in range(len(DIRECTIONS)):
            problem.set_initial_value(
                problem.fluent(DIRECTION_CONDITIONS[i])(direction_objects[i]),
                True
            )

        # right-rot(?d ?dn) for all directions, where dn is the direction to the right := true
        for i in range(len(DIRECTIONS)):
            problem.set_initial_value(
                problem.fluent(RIGHT_ROT)(
                    direction_objects[i],
                    direction_objects[i + 1 if i + 1 < len(DIRECTIONS) else 0]
                ),
                True
            )

        # left-rot(?d ?dn) for all directions, where dn is the direction to the left := true
        for i in range(len(DIRECTIONS)):
            problem.set_initial_value(
                problem.fluent(LEFT_ROT)(
                    direction_objects[i],
                    direction_objects[i - 1 if i - 1 >= 0 else len(DIRECTIONS) - 1]
                ),
                True
            )

        # facing(?d) ?d = north := true
        problem.set_initial_value(
            problem.fluent(FACING)(direction_objects[0]),
            True
        )

        # Start position
        s_x, s_y = self._start.get_position()

        # at(?x ?y) ?x = s_x, ?y = s_y := true
        problem.set_initial_value(
            problem.fluent(AT)(x_objects[s_x], y_objects[s_y]),
            True
        )

        # Goal position
        g_x, g_y = self._goal.get_position()

        # Goal state: at(g_x g_y)
        problem.add_goal(
            problem.fluent(AT)(x_objects[g_x], y_objects[g_y])
        )

        return problem

    def generate_flattened_problem(self, problem_name: str):

        # Problem set-up
        reader = PDDLReader()
        problem = reader.parse_problem("flattened_maze.pddl")
        problem.name = problem_name

        objects = []
        pointer = 0

        available_positions = [t.get_position() for t in self._maze]
        available_positions.insert(0, available_positions.pop(available_positions.index(self._start.get_position())))

        for p in available_positions:

            a = "s" if p == self._start.get_position() else f"x{pointer}"
            objects.append(Object(a, problem.user_type(POSITION)))
            pointer += 1

            if (p[0], p[1] + 1) in available_positions:
                b = f"x{pointer}"
                available_positions.remove(available_positions.index((p[0], p[1] + 1)))
                objects.append(Object(f"x{pointer}", problem.user_type(POSITION)))
                pointer += 1
                problem.set_initial_value(problem.fluent(PATH)(curr, ), True)
            if (p[0], p[1] - 1) in available_positions:
                available_positions.remove(available_positions.index((p[0], p[1] - 1)))
                objects.append(Object(f"x{pointer}", problem.user_type(POSITION)))
                pointer += 1
                problem.set_initial_value(
                    problem.fluent(INC)(x_objects[i - 1], x_objects[i]),
                    True
                )
            if (p[0] + 1, p[1]) in available_positions:
                available_positions.remove(available_positions.index((p[0] + 1, p[1])))
                objects.append(Object(f"r{pointer}", problem.user_type(POSITION)))
                pointer += 1
                problem.set_initial_value(
                    problem.fluent(INC)(x_objects[i - 1], x_objects[i]),
                    True
                )
            if (p[0] - 1, p[1]) in available_positions:
                available_positions.remove(available_positions.index((p[0] - 1, p[1])))
                objects.append(Object(f"l{pointer}", problem.user_type(POSITION)))
                pointer += 1
                problem.set_initial_value(
                    problem.fluent(INC)(x_objects[i - 1], x_objects[i]),
                    True
                )

        for tile in self._maze:
            x, y = tile.get_position()
            print(x, y)

    def dfs(self, problem: Problem, visited: list, current_tile: Tile, current_object: Object):
        visited.append(current_tile)
        current_position = current_tile.get_position()
        neighbour_map = {
            f"u{self._pointer}": self._find_tile((current_position[0], current_position[0] - 1)),
            f"d{self._pointer}": self._find_tile((current_position[0], current_position[0] + 1)),
            f"l{self._pointer}": self._find_tile((current_position[0] - 1, current_position[0])),
            f"r{self._pointer}": self._find_tile((current_position[0] + 1, current_position[0])),
        }
        for i, neighbour in enumerate(neighbour_map.values()):
            if neighbour is not None and neighbour not in visited:
                neighbour_object = Object(list(neighbour_map.keys())[i], problem.user_type(POSITION))
                problem.add_object(neighbour_object)
                problem.set_initial_value(problem.fluent(PATH)(current_object, neighbour_object), True)
                problem.set_initial_value(problem.fluent(PATH)(neighbour_object, current_object), True)
                self.dfs(problem, visited, neighbour, neighbour_object)

    def _find_tile(self, neighbour_position):
        signal = [p for p in self._maze if p.get_position() == neighbour_position]
        return signal[0] if signal else None


def export(problem, directory: str) -> None:
    """
    Exports the problem saved in current object to a PDDL file.
    :param problem: problem
    :param directory: The directory of the PDDL file.
    """
    writer = PDDLWriter(problem)
    writer.write_problem(f"{directory}/{problem.name}.pddl")
