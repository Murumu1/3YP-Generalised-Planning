from unified_planning.model import Problem, Object
from util.maze_utils import MazeProblemGenerator, Maze
# from typing import override
from util.constants import *
from util.tile import Tile


class ComplexProblemGenerator(MazeProblemGenerator):
    def __init__(self, problem_count: int):
        super().__init__(problem_count)

    # @override
    def _generate_problem(self, maze: Maze) -> Problem:
        problem = self._reader.parse_problem("domains/maze.pddl")
        problem.name = "maze_problem"

        # Create objects
        x_objects = [Object(f"x{i}", problem.user_type(POSITION)) for i in range(TILE_COUNT)]
        y_objects = [Object(f"y{i}", problem.user_type(POSITION)) for i in range(TILE_COUNT)]
        direction_objects = [Object(direction, problem.user_type("direction")) for direction in DIRECTIONS]
        problem.add_objects(x_objects + y_objects + direction_objects)

        # Set initial value for fluents
        # inc(?a ?b) from x0->x9, y0->y9 := true
        for i in range(1, TILE_COUNT):
            problem.set_initial_value(problem.fluent(INC)(x_objects[i - 1], x_objects[i]), True)
            problem.set_initial_value(problem.fluent(INC)(y_objects[i - 1], y_objects[i]), True)

        # dec(?a ?b) from x9->x0 y9->y0 := true
        for i in range(1, TILE_COUNT):
            problem.set_initial_value(problem.fluent(DEC)(x_objects[i], x_objects[i - 1]), True)
            problem.set_initial_value(problem.fluent(DEC)(y_objects[i], y_objects[i - 1]), True)

        # path(?x ?y) for all tiles in maze := true
        for tile in maze.tiles:
            x, y = tile.get_position()
            problem.set_initial_value(problem.fluent(PATH)(x_objects[x], y_objects[y]), True)

        # is-{d}(?d) for all directions := true
        for i in range(len(DIRECTIONS)):
            problem.set_initial_value(problem.fluent(DIRECTION_CONDITIONS[i])(direction_objects[i]), True)

        # right-rot(?d ?dn) for all directions, where dn is the direction to the right := true
        for i in range(len(DIRECTIONS)):
            problem.set_initial_value(problem.fluent(RIGHT_ROT)(
                direction_objects[i],
                direction_objects[i + 1 if i + 1 < len(DIRECTIONS) else 0]
            ), True)

        # left-rot(?d ?dn) for all directions, where dn is the direction to the left := true
        for i in range(len(DIRECTIONS)):
            problem.set_initial_value(problem.fluent(LEFT_ROT)(
                direction_objects[i],
                direction_objects[i - 1 if i - 1 >= 0 else len(DIRECTIONS) - 1]
            ), True)

        # facing(?d) ?d = north := true
        problem.set_initial_value(problem.fluent(FACING)(direction_objects[0]), True)

        # Start position
        # at(?x ?y) ?x = s_x, ?y = s_y := true
        s_x, s_y = maze.start.get_position()
        problem.set_initial_value(problem.fluent(AT)(x_objects[s_x], y_objects[s_y]), True)

        # Goal position
        # goal: at(g_x g_y)
        g_x, g_y = maze.goal.get_position()
        problem.add_goal(problem.fluent(AT)(x_objects[g_x], y_objects[g_y]))

        return problem


# TODO: Ensure that there can be multiple paths
class PartiallySolvedProblemGenerator(MazeProblemGenerator):
    def __init__(self, problem_count: int):
        super().__init__(problem_count)

        self._pointer = 0
        self._current_maze = None
        self._current_problem = None
        self._current_visited = []

    # @override
    def _generate_problem(self, maze: Maze) -> Problem:
        self._current_maze = maze
        self._current_visited = []
        self._pointer = 0

        # Problem set-up
        self._current_problem = self._reader.parse_problem("domains/flattened_maze.pddl")
        self._current_problem.name = "maze_problem"
        start_object = Object("start", self._current_problem.user_type(POSITION))
        self._current_problem.add_object(start_object)
        self._current_problem.set_initial_value(self._current_problem.fluent(AT)(start_object), True)

        self._dfs(self._current_maze.start, start_object)
        return self._current_problem

    # Performs depth-first search to locate paths along the maze
    def _dfs(self, current_tile: Tile, current_object: Object):

        # Ensure no tile is visited twice
        self._current_visited.append(current_tile)
        current_position = current_tile.get_position()

        # Mapping of potential neighbour positions to maze tiles
        neighbour_map = {
            f"u{self._pointer}": self._find_tile((current_position[0], current_position[1] - 1)),
            f"d{self._pointer}": self._find_tile((current_position[0], current_position[1] + 1)),
            f"l{self._pointer}": self._find_tile((current_position[0] - 1, current_position[1])),
            f"r{self._pointer}": self._find_tile((current_position[0] + 1, current_position[1])),
        }

        for i, neighbour in enumerate(neighbour_map.values()):
            if neighbour is not None and neighbour not in self._current_visited:

                # Create object for neighbour tile
                neighbour_object = Object(list(neighbour_map.keys())[i], self._current_problem.user_type(POSITION))
                self._current_problem.add_object(neighbour_object)

                # path(?x ?xn) to and fro neighbouring tiles := true
                self._current_problem.set_initial_value(
                    self._current_problem.fluent(PATH)(current_object, neighbour_object), True)
                self._current_problem.set_initial_value(
                    self._current_problem.fluent(PATH)(neighbour_object, current_object), True)

                # Set goal to at(neighbour) if it's the goal tile
                if neighbour.get_position() == self._current_maze.goal.get_position():
                    self._current_problem.add_goal(self._current_problem.fluent(AT)(neighbour_object))

                # Avoid repeating object names
                self._pointer += 1
                self._dfs(neighbour, neighbour_object)

    # Locates the tile object given its position in the maze
    def _find_tile(self, neighbour_position):
        signal = [p for p in self._current_maze.tiles if p.get_position() == neighbour_position]
        return signal[0] if signal else None
