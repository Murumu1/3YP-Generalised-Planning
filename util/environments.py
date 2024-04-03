from dataclasses import dataclass
from util.tile import Tile, TileCollection


class Environment:
    pass


@dataclass
class MazeEnvironment(Environment):
    tiles: TileCollection
    start: Tile
    goal: Tile


@dataclass
class SnakeEnvironment(Environment):
    board: TileCollection
    start: Tile
    apples: TileCollection
