from collections import UserList
from constants import WIDTH, HEIGHT
from dataclasses import dataclass
from options import OptionManager
import pygame


class EnvironmentObject:
    pass


class Tile(EnvironmentObject):

    def __init__(self, **position):
        """
        Tile object for compiling locations and Pygame attributes.
        Arguments:
            position: Input position which can be

                - The Tile position in Cartesian coordinates (tile_position=).
                - The Tile position in Pygame coordinates (pygame_position=).
                - Or an existing Tile object (tile=).

        At least one must be specified.
        """

        self._option_manager = OptionManager()
        self._tile_size = self._option_manager.get_tile_size()
        self._tile_width, self._tile_height = (
            WIDTH // self._tile_size,
            HEIGHT // self._tile_size
        )
        
        self._tile_position = tuple[int, int]()
        if not any(self._is_tile_like(val) for val in position.values()):
            raise TypeError("No valid arguments found.")
        self.set_position(**position)

    def _is_tile_like(self, instance):
        return self._is_point(instance) or isinstance(instance, Tile)

    @staticmethod
    def _is_point(instance):
        return isinstance(instance, tuple) and list(map(type, instance)) == [int, int]

    def set_position(self, **position) -> None:
        """
        Sets the position of the tile.

        Arguments:
            position: Input position which can be

                - The Tile position in Cartesian coordinates (tile_position=).
                - The Tile position in Pygame coordinates (pygame_position=).
                - Or an existing Tile object (tile=).

        At least one must be specified.
        """
        tile_position = position.get("tile_position")
        pygame_position = position.get("pygame_position")
        tile = position.get("tile")

        if pygame_position is not None:
            self._tile_position = (
                pygame_position[0] // self._tile_width,
                pygame_position[1] // self._tile_height
            )

        elif self._tile_position is not None:
            self._tile_position = tile_position

        elif tile is not None:
            self._tile_position = tile.get_position()

    def get_position(self) -> tuple[int, int]:
        """Returns the position of the tile in tile coordinates"""
        return self._tile_position

    def get_rect(self) -> pygame.Rect:
        """Returns the pygame.Rect object of the tile"""
        return pygame.Rect(
            self._tile_position[0] * self._tile_width,
            self._tile_position[1] * self._tile_height,
            self._tile_width,
            self._tile_height
        )

    def get_neighbours(self) -> list[tuple[int, int]]:
        neighbours = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        positions = [
            (x + self._tile_position[0], y + self._tile_position[1])
            for x, y in neighbours
        ]
        return [p for p in positions if all(0 <= q < self._tile_size for q in p)]

    # Tiles are equal if they have the same position
    def __eq__(self, other) -> bool:
        if isinstance(other, Tile):
            return self._tile_position == other.get_position()
        elif self._is_point(other):
            return self._tile_position == other
        return False

    def __hash__(self):
        return hash(self._tile_position)


class TileCollection(UserList[Tile]):

    def __init__(self, iterable=None):
        if iterable is None:
            self.data = []
        else:
            super().__init__(self._ensure_tile(item) for item in iterable)

    def __setitem__(self, index, item):
        self.data[index] = self._ensure_tile(item)

    def insert(self, index, item):
        self.data.insert(index, self._ensure_tile(item))

    def append(self, item):
        self.data.append(self._ensure_tile(item))

    def extend(self, other):
        if isinstance(other, type(self)):
            self.data.extend(other)
        else:
            self.data.extend(self._ensure_tile(item) for item in other)

    @staticmethod
    def _ensure_tile(instance):
        if isinstance(instance, Tile):
            return instance
        raise TypeError(f"Tile object expected, instead got {type(instance).__name__}")

    def find_tile(self, position: tuple[int, int]) -> Tile:
        signal = [tile for tile in self.data if tile.get_position() == position]
        return signal[0] if signal else None

    def find_neighbours(self, tile: Tile) -> 'TileCollection':
        possible_neighbours = tile.get_neighbours()
        valid_neighbours = []
        for i, neighbour in enumerate(possible_neighbours):
            if self.find_tile(neighbour):
                valid_neighbours.append(neighbour)
        return TileCollection([self.find_tile(valid_neighbour) for valid_neighbour in valid_neighbours])


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