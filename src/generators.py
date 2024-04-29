"""
**Path finding Problem Generators**

This module provides classes for generating various types of problems suitable for unified planning frameworks.

Classes:
    - ``ProblemGenerator``: Parent class for all problem generators, providing an interface for GUI and PDDL problem creation.
    - ``BlocklyMazeProblemGenerator``: Generates maze problems similar to Blockly games maze problems.
    - ``DirectionalProblemReducedMazeProblemGenerator``: Generates maze problems with only a move action, inferring direction.
    - ``NonDirectionalProblemReducedMazeProblemGenerator``: Generates maze problems with only a move action, using location-based objects.
    - ``SnakeProblemGenerator``: Generates snake problems.

Example usage::

    # Create a Blockly maze problem generator
    blockly_maze_generator = BlocklyMazeProblemGenerator(problem_count=5)

    # Save the generated problems as PDDL files
    maze_problem.save_as_pddl()

    # Display information about the generated problems
    maze_problem.display_problems()

    # Display images of the generated environments as plots
    maze_problem.display_images()

    # Solve each problem individually using classical planning
    maze_problem.solve_each()

    # Solve all problems at once using generalised planning
    maze_problem.solve_all()
"""

import os.path
import shutil
import random
import glob
import math
import unified_planning as up
from typing import Union
from unified_planning.engines import CompilationKind, PlanGenerationResultStatus
from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.model import Problem, Object
from unified_planning.shortcuts import OneshotPlanner, get_environment, Not
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from src.environment import *
from src.constants import *
from options import OptionManager
from src.validators import non_negative_and_non_zero


class ProblemGenerator:

    def __init__(self, domain_path, **options):
        """
        Parent class for all problem generators.
        Provides an interface for GUI and PDDL problem creation.

        Arguments:
            domain_path (str): Path to PDDL domain file
            **options: Additional options for problem generation.
        """

        self._domain = domain_path
        self._reader = PDDLReader()
        self._option_manager = OptionManager()
        self._set_arguments(**options)
        self._set_problems()
        get_environment().credits_stream = None

    @non_negative_and_non_zero
    def _set_arguments(self, **options) -> None:

        # Problem generation
        self._auto: bool = options.get("auto", False)
        self._problem_count: int = options.get("problem_count", 10)
        self._program_lines: int = options.get("program_lines", 10)
        self._tile_size: int = options.get("tile_size", 5)
        self._option_manager.set_tile_size(self._tile_size)
        self._screen_length = self._option_manager.get_screen_length()
        self._screen_size = self._screen_length, self._screen_length

        # File management
        self._image_directory: str = options.get("image_directory", "../../images_temp")
        self._plan_directory: str = options.get("plan_directory", "../../plan_temp")
        self._problem_directory: str = options.get("problem_directory", "problem_temp")

    def _set_problems(self) -> None:
        """Generates environments and problems."""

        # Ensure image directory is clear before processing
        self._clear_directory(self._image_directory)

        self._problems: list[Problem] = []
        self._environments: list[Environment] = []
        for i in range(self._problem_count):
            pygame.init()
            environment = self._generate_environment()
            self._environments.append(environment)
            self._add_problem(environment)

    @staticmethod
    def _clear_directory(directory):

        # Recreates a path to directory
        if os.path.isdir(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

    def _generate_environment_manual(self) -> Environment:
        """Manual generation for environments."""
        pass

    def _generate_environment_auto(self) -> Environment:
        """Automatic generation for environments."""
        pass

    def _generate_environment(self) -> Environment:
        return self._generate_environment_auto() if self._auto else self._generate_environment_manual()

    def _add_problem(self, environment: Environment) -> None:
        """
        Creates a PDDL problem and adds it to the problem collection.

        Arguments:
            environment (Environment): Environment describing the current problem.
        """

        self._obj_map = {}
        self._problem = self._reader.parse_problem(f"domains/{self._domain}.pddl")
        self._problem.name = f"{self._domain}{len(self._problems)}"
        self._setup_problem(environment)
        self._problems.append(self._problem)
        print("[DEBUG] problem added")

    def _setup_problem(self, environment: Environment) -> None:
        """
        Sets up a PDDL problem.

        Arguments:
            environment (Environment): Environment describing the current problem.
        """

        raise NotImplementedError

    def _add_mapping(self, env_obj: EnvironmentObject, *pddl_objects: Object) -> None:
        """
        Adds mapping between environment objects and PDDL objects.

        Arguments:
            env_obj (EnvironmentObject): Environment object.
            *pddl_objects (Object): PDDL objects.
        """

        eo_hash = hash(env_obj)
        pddl_objects = list(pddl_objects)
        observed_mapping = self._obj_map.get(eo_hash)
        if observed_mapping:
            self._obj_map[eo_hash].extend(pddl_objects)
        else:
            self._obj_map[eo_hash] = pddl_objects

    def _get_mapping(self, env_obj: EnvironmentObject) -> Union[Object, list[Object]]:
        """
        Retrieves mapping for a given environment object.

        Arguments:
            env_obj (EnvironmentObject): Environment object.

        Returns:
            Union[Object, list[Object]]: PDDL object or list of PDDL objects.
        """

        eo_hash = hash(env_obj)
        mapping = self._obj_map.get(eo_hash, [])
        if len(mapping) == 1:
            return mapping[0]
        return mapping

    def _save_pygame_environment(self, screen: pygame.Surface):
        """
        Saves a Pygame surface as an image.

        Arguments:
            screen (pygame.Surface): Pygame screen.
        """

        if not os.path.exists(self._image_directory):
            os.makedirs(self._image_directory)

        pygame.image.save(screen, f"{self._image_directory}/{self._domain}{len(self._environments)}.jpg")
        print(f"[DEBUG] {self._domain} environment generated successfully")

    def save_as_pddl(self) -> None:
        """Saves the generated problems as PDDL files."""

        self._clear_directory(self._problem_directory)
        for problem in self._problems:
            file_path = f"{self._problem_directory}/{problem.name}.pddl"
            open(file_path, 'a').close()
            writer = PDDLWriter(problem)
            writer.write_problem(file_path)

    def display_problems(self) -> None:
        """Displays information about the generated problems."""

        for i, problem in enumerate(self._problems):
            print(f"Problem {i}:")
            print(problem)

    def display_images(self, columns=None) -> None:
        """Displays images of the generated environments as iPython plots."""

        images = []
        for img_path in glob.glob(f"{self._image_directory}/*.jpg"):
            images.append(mpimg.imread(img_path))

        plt.figure(figsize=(20, 10))

        columns = math.floor(math.sqrt(len(images))) if not columns else columns
        for i, image in enumerate(images):
            plt.subplot(len(images) // columns + 1, columns, i + 1)
            plt.imshow(image)
            plt.axis("off")

    def solve_each(self) -> list:
        """
        Solves each problem individually using classical planning.

        Returns:
            list: A list containing information about the results of solving each problem.
        """

        results = []
        for i, problem in enumerate(self._problems):
            print(f"Plan {i + 1}:")

            with OneshotPlanner(problem_kind=problem.kind) as planner:
                result = planner.solve(problem)
                print(f"Status: {result.status}")

                if result.status == up.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
                    print(f"Found plan with {len(result.plan.actions)} steps!")
                    for j, action in enumerate(result.plan.actions):
                        print(f"{j}: {action}")
                    results.append(result)

                else:
                    print("Unable to find a plan.")

            print("")

        return results

    def solve_all(self, program_lines=10) -> list[PlanGenerationResultStatus]:
        """Solves all problems at once using generalised planning

        Returns:
            list[PlanGenerationResultStatus]: A list containing information about the results of solving each problem.
        """

        with up.environment.get_environment().factory.FewshotPlanner(name="bfgp") as planner:
            planner.set_arguments(
                program_lines=program_lines if self._program_lines == 10 else self._program_lines,
                theory="cpp",
                # translated_problem_dir=self._plan_directory + "/"
            )

            results = planner.solve(self._problems, output_stream=None)
            if all(r == PlanGenerationResultStatus.SOLVED_SATISFICING for r in results):
                print("Plan found successfully")

            return results


class _MazeProblemGenerator(ProblemGenerator):

    def __init__(self, domain_path, **options):
        """
        Generates maze problems as MazeEnvironment instances.
        Inherits from ProblemGenerator.

        Arguments:
            domain_path (str): Path to the domain.
            **options: Additional options for problem generation.
        """

        super().__init__(domain_path, **options)

    @staticmethod
    def _change_special_tile(screen: pygame.Surface,
                             special_tile: Tile,
                             conflict_tile: Tile,
                             new_tile: Tile,
                             colour: tuple) -> tuple:
        """
        Changes the start/goal tile on the maze.

        Arguments:
            screen (pygame.Surface): Pygame screen.
            special_tile (Tile): The special tile to change.
            conflict_tile (Tile): The conflicting tile.
            new_tile (Tile): The new tile to be set as special.
            colour (tuple): RGB color tuple for drawing the tile.

        Returns:
            tuple: Updated special tile and conflict tile.
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

    def _generate_environment_manual(self) -> MazeEnvironment:
        """
        Generates maze environment manually.

        Returns:
            MazeEnvironment: Generated maze environment.
        """

        # Display set-up.
        pygame.init()
        screen = pygame.display.set_mode(self._screen_size)
        clock = pygame.time.Clock()
        screen.fill(BACKGROUND)
        maze_generated = False

        # Maze set-up.
        maze = TileCollection()
        goal = None
        start = None

        # Determines what tile is modified on right click.
        to_change = START

        while not maze_generated:
            for event in pygame.event.get():

                # Exit if enter is pressed or when the window is closed.
                if event.type == pygame.QUIT:
                    maze_generated = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        maze_generated = True

                if event.type == pygame.MOUSEBUTTONDOWN:

                    # Tile at cursor position
                    current_tile = Tile(pygame_position=pygame.mouse.get_pos())

                    # Left click modifies visibility of a tile on the screen.
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

                    # Right click add/changes the start/goal tile.
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

        self._save_pygame_environment(screen)
        pygame.quit()

        return MazeEnvironment(maze, start, goal)

    def _generate_environment_auto(self) -> MazeEnvironment:
        """
        Generates maze environment automatically.

        Returns:
            MazeEnvironment: Generated maze environment.
        """

        # Maze set-up.
        maze = TileCollection()
        screen = pygame.display.set_mode(self._screen_size)
        screen.fill(BACKGROUND)
        available_locations = [(x, y) for x in range(self._tile_size) for y in range(self._tile_size)]

        # Selects the start and goal locations randomly.
        start_location, goal_location = random.sample(available_locations, 2)
        start = Tile(tile_position=start_location)
        goal = Tile(tile_position=goal_location)
        maze.extend([start, goal])
        pygame.draw.rect(screen, START_TILE, start.get_rect())
        pygame.draw.rect(screen, GOAL_TILE, goal.get_rect())
        pygame.display.flip()

        # Iteratively chooses a random neighbour until a path has been created.
        current_tile = start
        while True:
            current_tile = Tile(tile_position=random.choice(current_tile.get_neighbours()))
            if current_tile == goal:
                break
            if current_tile not in maze:
                maze.append(current_tile)
                pygame.draw.rect(screen, FILLED_TILE, current_tile.get_rect())
                pygame.display.flip()

        self._save_pygame_environment(screen)
        pygame.quit()

        return MazeEnvironment(maze, start, goal)


class BlocklyMazeProblemGenerator(_MazeProblemGenerator):
    def __init__(self, **options):
        """
        Generates maze problems in a similar fashion to Blockly games maze problems.

        Arguments:
            **options: Additional options for problem generation.
        """

        super().__init__("maze", **options)

    def _setup_problem(self, maze: MazeEnvironment) -> None:

        # Create objects
        x_objects = [Object(f"x{i}", self._problem.user_type(POSITION)) for i in range(self._tile_size)]
        y_objects = [Object(f"y{i}", self._problem.user_type(POSITION)) for i in range(self._tile_size)]
        direction_objects = [Object(direction, self._problem.user_type("direction")) for direction in DIRECTIONS]
        self._problem.add_objects(x_objects + y_objects + direction_objects)

        # Set initial value for fluents
        # inc(?a ?b) from x0->x9, y0->y9 := true
        for i in range(1, self._tile_size):
            self._problem.set_initial_value(self._problem.fluent(INC)(x_objects[i - 1], x_objects[i]), True)
            self._problem.set_initial_value(self._problem.fluent(INC)(y_objects[i - 1], y_objects[i]), True)

        # dec(?a ?b) from x9->x0 y9->y0 := true
        for i in range(1, self._tile_size):
            self._problem.set_initial_value(self._problem.fluent(DEC)(x_objects[i], x_objects[i - 1]), True)
            self._problem.set_initial_value(self._problem.fluent(DEC)(y_objects[i], y_objects[i - 1]), True)

        # path(?x ?y) for all tiles in maze := true
        for tile in maze.tiles:
            x, y = tile.get_position()
            self._problem.set_initial_value(self._problem.fluent(PATH)(x_objects[x], y_objects[y]), True)

        # is-{d}(?d) for all directions := true
        for i in range(len(DIRECTIONS)):
            self._problem.set_initial_value(self._problem.fluent(DIRECTION_CONDITIONS[i])(direction_objects[i]), True)

        # right-rot(?d ?dn) for all directions, where dn is the direction to the right := true
        for i in range(len(DIRECTIONS)):
            self._problem.set_initial_value(self._problem.fluent(RIGHT_ROT)(
                direction_objects[i],
                direction_objects[i + 1 if i + 1 < len(DIRECTIONS) else 0]
            ), True)

        # left-rot(?d ?dn) for all directions, where dn is the direction to the left := true
        for i in range(len(DIRECTIONS)):
            self._problem.set_initial_value(self._problem.fluent(LEFT_ROT)(
                direction_objects[i],
                direction_objects[i - 1 if i - 1 >= 0 else len(DIRECTIONS) - 1]
            ), True)

        # facing(?d) ?d = north := true
        self._problem.set_initial_value(self._problem.fluent(FACING)(direction_objects[0]), True)

        # start: at(?s_x ?s_y) := true
        s_x, s_y = maze.start.get_position()
        self._problem.set_initial_value(self._problem.fluent(AT)(x_objects[s_x], y_objects[s_y]), True)

        # goal: at(g_x g_y)
        g_x, g_y = maze.goal.get_position()
        self._problem.add_goal(self._problem.fluent(AT)(x_objects[g_x], y_objects[g_y]))


class DirectionalProblemReducedMazeProblemGenerator(_MazeProblemGenerator):
    def __init__(self, **options):
        """
        Generates maze problems with only a move action.
        Objects are named in a way so that direction of travel can be inferred

        Arguments:
            **options: Additional options for problem generation.
        """

        super().__init__("reduced_maze", **options)

    def _setup_problem(self, maze: MazeEnvironment) -> None:

        self._maze = maze

        # Counter to ensure no object name is repeated
        self._counter = 0

        # Object set-up
        self._start_object = Object("start", self._problem.user_type(POSITION))
        self._goal_object = Object("goal", self._problem.user_type(POSITION))
        self._problem.add_object(self._start_object)
        self._problem.add_object(self._goal_object)
        self._problem.set_initial_value(self._problem.fluent(AT)(self._start_object), True)
        self._problem.add_goal(self._problem.fluent(AT)(self._goal_object))
        self._dfs(self._maze.start, self._start_object)

    def _dfs(self, current_tile: Tile, current_object: Object):

        # Ensure no tile is visited twice
        self._add_mapping(current_tile, current_object)
        current_position = current_tile.get_position()

        # Mapping of potential neighbour positions to maze tiles
        neighbour_map = {
            f"u{self._counter}": self._maze.tiles.find_tile((current_position[0], current_position[1] - 1)),
            f"d{self._counter}": self._maze.tiles.find_tile((current_position[0], current_position[1] + 1)),
            f"l{self._counter}": self._maze.tiles.find_tile((current_position[0] - 1, current_position[1])),
            f"r{self._counter}": self._maze.tiles.find_tile((current_position[0] + 1, current_position[1])),
        }

        for direction, neighbour in neighbour_map.items():

            # If there is an existing object for the neighbour with the same direction: re-use it.
            if neighbour is not None:
                existing_mapping = [
                    obj for obj in self._get_mapping(neighbour)
                    if obj.name[0] == direction[0] or obj == self._start_object or obj == self._goal_object
                ]
                if existing_mapping:
                    self._problem.set_initial_value(
                        self._problem.fluent(PATH)(current_object, existing_mapping[0]), True
                    )
                    continue

                # Create object for neighbour tile
                if neighbour == self._maze.start:
                    neighbour_object = self._start_object
                elif neighbour == self._maze.goal:
                    neighbour_object = self._goal_object
                else:
                    neighbour_object = Object(direction, self._problem.user_type(POSITION))
                    self._problem.add_object(neighbour_object)

                # path(?x ?xn) to neighbour tile (xn) := true
                self._problem.set_initial_value(
                    self._problem.fluent(PATH)(current_object, neighbour_object), True
                )

                # Avoid repeating object names
                self._counter += 1
                self._dfs(neighbour, neighbour_object)

    def _get_mapping(self, env_obj: Tile) -> list[Object]:

        # Modified to ensure output is always a list
        eo_hash = hash(env_obj)
        mapping = self._obj_map.get(eo_hash, [])
        return mapping


class NonDirectionalProblemReducedMazeProblemGenerator(_MazeProblemGenerator):
    def __init__(self, **options):
        """
        Generates maze problems with only a move action.
        Objects are the location of the tiles in the maze.

        Arguments:
            **options: Additional options for problem generation.
        """

        super().__init__("reduced_maze", **options)

    def _setup_problem(self, maze: MazeEnvironment) -> None:

        # Maps all tiles to PDDL objects.
        for tile in maze.tiles:
            position = tile.get_position()
            tile_obj = Object(f"p{position[0]}-{position[1]}", self._problem.user_type(POSITION))
            self._add_mapping(tile, tile_obj)
            self._problem.add_object(tile_obj)

        # Creates all required valid paths between tiles.
        for tile in maze.tiles:
            for neighbour in maze.tiles.find_neighbours(tile):
                neighbour_object = self._get_mapping(neighbour)
                current_object = self._get_mapping(tile)
                self._problem.set_initial_value(self._problem.fluent(PATH)(neighbour_object, current_object), True)
                self._problem.set_initial_value(self._problem.fluent(PATH)(current_object, neighbour_object), True)

        start_object = self._get_mapping(maze.start)
        goal_object = self._get_mapping(maze.goal)

        self._problem.set_initial_value(self._problem.fluent(AT)(start_object), True)
        self._problem.add_goal(self._problem.fluent(AT)(goal_object))


class SnakeProblemGenerator(ProblemGenerator):

    def __init__(self, **options):
        """
        Generates snake problems.
        Inherits from ProblemGenerator.

        Arguments:
            **options: Additional options for problem generation.
        """

        self._apple_count = options.get("apple_count", 5)
        super().__init__("snake", **options)

        ratio = self._apple_count / ((self._tile_size ** 2) - 2)
        if ratio > 1:
            raise ValueError(f"Too many apples! apples must be less than: {((self._tile_size ** 2) - 2)} for the "
                             f"selected tile size: {self._tile_size}")

    def _generate_environment_auto(self) -> Environment:
        """
        Generates snake environment automatically.

        Returns:
            Environment: Generated snake environment.
        """

        board = TileCollection(
            [Tile(tile_position=(x, y)) for x in range(self._tile_size) for y in range(self._tile_size)]
        )
        available_locations = board.copy()

        # Selects a random start position and random positions for apples.
        start = available_locations.pop(random.randint(0, len(available_locations) - 1))
        tail = available_locations.find_neighbours(start)[0]
        available_locations.remove(tail)

        goals = random.sample(available_locations, self._apple_count)
        apples = TileCollection(goals)

        screen = pygame.display.set_mode(self._screen_size)
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
        pygame.draw.rect(screen, TAIL_TILE, tail.get_rect())
        pygame.display.flip()

        self._save_pygame_environment(screen)
        pygame.quit()

        return SnakeEnvironment(board, start, tail, apples)

    def _generate_environment_manual(self) -> Environment:
        """
        Generates snake environment manually.

        Returns:
            Environment: Generated snake environment.
        """
        pass

    def _setup_problem(self, environment: SnakeEnvironment) -> None:

        # Maps all tiles to PDDL objects.
        for tile in environment.board:
            position = tile.get_position()
            tile_obj = Object(f"p{position[0]}-{position[1]}", self._problem.user_type(POSITION))
            self._add_mapping(tile, tile_obj)
            self._problem.add_object(tile_obj)

        # Creates all required valid paths between tiles.
        for tile in environment.board:
            for neighbour in environment.board.find_neighbours(tile):
                neighbour_object = self._get_mapping(neighbour)
                current_object = self._get_mapping(tile)
                self._problem.set_initial_value(self._problem.fluent(PATH)(neighbour_object, current_object), True)
                self._problem.set_initial_value(self._problem.fluent(PATH)(current_object, neighbour_object), True)

        start_object = self._get_mapping(environment.head)

        # Tail is set to a random neighbour of the head.
        tail_tile = environment.tail
        tail_object = self._get_mapping(tail_tile)

        # Body.
        self._problem.set_initial_value(self._problem.fluent(HEAD_AT)(start_object), True)
        self._problem.set_initial_value(self._problem.fluent(TAIL_AT)(tail_object), True)
        self._problem.set_initial_value(self._problem.fluent(BODY_CON)(start_object, tail_object), True)

        # Blocked locations.
        self._problem.set_initial_value(self._problem.fluent(BLOCKED)(start_object), True)
        self._problem.set_initial_value(self._problem.fluent(BLOCKED)(tail_object), True)

        # Apple locations.
        self._problem.set_initial_value(self._problem.fluent(APPLE_AT)(self._get_mapping(environment.apples[0])), True)
        self._problem.set_initial_value(
            self._problem.fluent(SPAWN_APPLE)(self._get_mapping(environment.apples[1])), True
        )

        # Final spawn once goal apple has been spawned.
        dummy_apple = Object(DUMMYPOINT, self._problem.user_type(POSITION))
        self._problem.add_object(dummy_apple)
        self._problem.set_initial_value(self._problem.fluent(IS_DUMMYPOINT)(dummy_apple), True)

        # next-apple(?appleloc ?nextappleloc) for all apples := true
        for i in range(1, len(environment.apples)):
            apple_obj = self._get_mapping(environment.apples[i])
            if i + 1 < len(environment.apples):
                next_apple_obj = self._get_mapping(environment.apples[i + 1])
            else:
                next_apple_obj = dummy_apple
            self._problem.set_initial_value(self._problem.fluent(NEXT_APPLE)(apple_obj, next_apple_obj), True)

        # goals += apple-at(?appleloc)
        for i in range(len(environment.apples)):
            self._problem.add_goal(Not(self._problem.fluent(APPLE_AT)(self._get_mapping(environment.apples[i]))))

    def _darken_colour(self, colour):
        """
        Darkens a given RGB color tuple.

        Arguments:
            colour (tuple): RGB color tuple.

        Returns:
            tuple: Darkened RGB color tuple.
        """

        ratio = 1 - (1 / self._apple_count)
        return round(colour[0] * ratio), round(colour[1] * ratio), round(colour[2] * ratio)
