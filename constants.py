# Colours
BACKGROUND = (255, 255, 255)
FILLED_TILE = (255, 255, 0)
GOAL_TILE = (0, 255, 0)
START_TILE = (255, 0, 0)
PLAYER = (0, 0, 255)

# Display
SCREEN_SIZE = WIDTH, HEIGHT = 500, 500

# Tile
TILE_COUNT = 5
TILE_SIZE = TILE_WIDTH, TILE_HEIGHT = (
    WIDTH // TILE_COUNT,
    HEIGHT // TILE_COUNT
)

# Flags
START = 'start'
GOAL = 'goal'

# Objects
DIRECTIONS = NORTH, EAST, SOUTH, WEST = 'north', 'east', 'south', 'west'

# Predicates
DIRECTION_CONDITIONS = IS_NORTH, IS_EAST, IS_SOUTH, IS_WEST = 'is-north', 'is-east', 'is-south', 'is-west'
POSITION = 'position'
INC = 'inc'
DEC = 'dec'
PATH = 'path'
RIGHT_ROT = 'right-rot'
LEFT_ROT = 'left-rot'
FACING = 'facing'
AT = 'at'
