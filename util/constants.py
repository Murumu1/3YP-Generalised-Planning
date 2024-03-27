# Colours
class ColoursConstants:
    BACKGROUND = (255, 255, 255)
    FILLED_TILE = (255, 255, 0)
    GOAL_TILE = (0, 255, 0)
    START_TILE = (255, 0, 0)
    PLAYER = (0, 0, 255)


# Display
class DisplayConstants:
    SCREEN_SIZE = WIDTH, HEIGHT = 500, 500


# Tile
class TileConstants:
    TILE_COUNT = 5
    TILE_SIZE = TILE_WIDTH, TILE_HEIGHT = (
        DisplayConstants.WIDTH // TILE_COUNT,
        DisplayConstants.HEIGHT // TILE_COUNT
    )


# Maze
class MazeConstants:

    # Image directory
    # TODO: Move to config.ini
    MAZE_DIRECTORY = "mazes"

    # Direction constants
    DIRECTIONS = NORTH, EAST, SOUTH, WEST = 'north', 'east', 'south', 'west'
    DIRECTION_CONDITIONS = IS_NORTH, IS_EAST, IS_SOUTH, IS_WEST = 'is-north', 'is-east', 'is-south', 'is-west'
    RIGHT_ROT = 'right-rot'
    LEFT_ROT = 'left-rot'
    FACING = 'facing'

    # Position constants
    POSITION = 'position'
    INC = 'inc'
    DEC = 'dec'
    PATH = 'path'
    AT = 'at'
    START = 'start'
    GOAL = 'goal'


class SnakeConstants:
    SNAKE_DIRECTORY = "snake"


