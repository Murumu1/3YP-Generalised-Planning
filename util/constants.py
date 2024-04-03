# Colours
BACKGROUND = (255, 255, 255)
FILLED_TILE = (255, 255, 0)
GOAL_TILE = (0, 255, 0)
START_TILE = (255, 0, 0)
PLAYER = (0, 0, 255)
INITIAL_APPLE = (0, 255, 0)


# Display
SCREEN_SIZE = WIDTH, HEIGHT = 500, 500


# Tile
TILE_COUNT = 5
TILE_SIZE = TILE_WIDTH, TILE_HEIGHT = (
    WIDTH // TILE_COUNT,
    HEIGHT // TILE_COUNT
)


# Maze
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

# Snake
SNAKE_DIRECTORY = "snake"

HEAD_AT = 'head-at'
TAIL_AT = 'tail-at'
BODY_CON = 'body-con'
BLOCKED = 'blocked'
APPLE_AT = 'apple-at'
NEXT_APPLE = 'next-apple'
SPAWN_APPLE = 'spawn-apple'
DUMMYPOINT = 'dummypoint'



