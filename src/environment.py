from collections import UserList
from dataclasses import dataclass
from options import OptionManager
import pygame


class EnvironmentObject:
    """Interface for objects to be used in environments."""
    pass


class Tile(EnvironmentObject):

    def __init__(self, **position: tuple[int, int]) -> None:
        """
        Tile object for compiling locations and Pygame attributes.

        Arguments:
            position: At least one must be specified:

                - The Tile position in Cartesian coordinates (tile_position=).
                - The Tile position in Pygame coordinates (pygame_position=).
                - Or an existing Tile object (tile=).
        """

        self._option_manager = OptionManager()
        self._tile_size = self._option_manager.get_tile_size()
        self._screen_length = self._option_manager.get_screen_length()
        self._tile_width, self._tile_height = (
            self._screen_length // self._tile_size,
            self._screen_length // self._tile_size
        )
        
        self._tile_position = tuple[int, int]()
        if not any(self._is_tile_like(val) for val in position.values()):
            raise TypeError("No valid arguments found.")
        self.set_position(**position)

    # Ensures the instance is a Tile object.
    def _is_tile_like(self, instance):
        return self._is_point(instance) or isinstance(instance, Tile)

    # Validates a tuple that corresponds to a position.
    @staticmethod
    def _is_point(instance):
        return isinstance(instance, tuple) and list(map(type, instance)) == [int, int]

    def set_position(self, **position) -> None:
        """
        Sets the position of the tile.

        Arguments:
            position: Input position which can be:

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
        """Obtains a list of all neighbours available from a Tile."""

        neighbours = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        positions = [
            (x + self._tile_position[0], y + self._tile_position[1])
            for x, y in neighbours
        ]
        return [p for p in positions if all(0 <= q < self._tile_size for q in p)]

    # Tiles are equal if they have the same position.
    def __eq__(self, other) -> bool:
        if isinstance(other, Tile):
            return self._tile_position == other.get_position()
        elif self._is_point(other):
            return self._tile_position == other
        return False

    # Tile hash is given by its position.
    def __hash__(self):
        return hash(self._tile_position)


class TileCollection(UserList[Tile]):
    def __init__(self, iterable=None):
        """
        A collection of Tile objects.

        Arguments:
            iterable (Iterable[Tile], optional): Optional list of Tile objects
        """
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

    # Ensures instance is a Tile object.
    @staticmethod
    def _ensure_tile(instance):
        if isinstance(instance, Tile):
            return instance
        raise TypeError(f"Tile object expected, instead got {type(instance).__name__}")

    def find_tile(self, position: tuple[int, int]) -> Tile:
        """
        Find a Tile object with the given position.

        Arguments:
            position (Tuple[int, int]): The position to search for.

        Returns:
            Tile: The Tile object found at the given position, or None if not found.
        """
        signal = [tile for tile in self.data if tile.get_position() == position]
        return signal[0] if signal else None

    def find_neighbours(self, tile: Tile) -> 'TileCollection':
        """
        Find neighboring Tile objects for a given Tile.

        Arguments:
            tile (Tile): The Tile object to find neighbors for.

        Returns:
            TileCollection: A collection of neighboring Tile objects.
        """
        possible_neighbours = tile.get_neighbours()
        valid_neighbours = []
        for i, neighbour in enumerate(possible_neighbours):
            if self.find_tile(neighbour):
                valid_neighbours.append(neighbour)
        return TileCollection([self.find_tile(valid_neighbour) for valid_neighbour in valid_neighbours])


class Environment:
    """Interface for environment classes."""
    pass


@dataclass
class MazeEnvironment(Environment):
    """
    A maze environment for defining a maze problem.

    Attributes:
        tiles (TileCollection): A collection of tiles composing the maze.
        start (Tile): The starting tile in the maze.
        goal (Tile): The goal tile in the maze.
    """
    tiles: TileCollection
    start: Tile
    goal: Tile


@dataclass
class SnakeEnvironment(Environment):
    """
    A snake environment for defining a snake problem.

    Attributes:
        board (TileCollection): A collection of tiles composing the game board.
        head (Tile): The head position of the snake.
        tail (Tile): The tail position of the snake.
        apples (TileCollection): A collection of tiles representing the positions of apples.
    """
    board: TileCollection
    head: Tile
    tail: Tile
    apples: TileCollection
