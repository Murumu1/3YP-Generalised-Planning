from util.constants import TILE_WIDTH, TILE_HEIGHT, TILE_COUNT
import pygame


class Tile:

    def __init__(self, **position):
        """
        Tile object for MazeProblemGenerator and MazePlanVisualiser.
        :param position: Position metrics: tile_position: tuple, pygame_position: tuple or tile: Tile
        """

        self._tile_position = tuple()
        self.set_position(**position)

    def set_position(self, **position) -> None:
        """
        Sets the position of the tile, at least one must be specified:
        :param position: Position metrics: tile_position: tuple, pygame_position: tuple or tile: Tile
        """

        tile_position = position.get("tile_position")
        pygame_position = position.get("pygame_position")
        tile = position.get("tile")

        if pygame_position is not None:
            self._tile_position = (
                pygame_position[0] // TILE_WIDTH,
                pygame_position[1] // TILE_HEIGHT
            )

        elif self._tile_position is not None:
            self._tile_position = tile_position

        elif tile is not None:
            self._tile_position = tile.get_position()

        else:
            raise ValueError("At least one of pygame_position, tile_position, tile must be specified and non-empty.")

    def get_position(self) -> tuple:
        """Returns the position of the tile in tile coordinates"""
        return self._tile_position

    def get_rect(self) -> pygame.Rect:
        """Returns the pygame.Rect object of the tile"""
        return pygame.Rect(
            self._tile_position[0] * TILE_WIDTH,
            self._tile_position[1] * TILE_HEIGHT,
            TILE_WIDTH,
            TILE_HEIGHT
        )

    def get_neighbours(self) -> list[tuple]:
        neighbours = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        positions = [
            (x + self._tile_position[0], y + self._tile_position[1])
            for x, y in neighbours
        ]
        return [p for p in positions if all(0 <= q < TILE_COUNT for q in p)]

    # Tiles are equal if they have the same position
    def __eq__(self, other) -> bool:
        if isinstance(other, Tile):
            return self._tile_position == other.get_position()
        return False

    def __hash__(self):
        return hash(self._tile_position)
