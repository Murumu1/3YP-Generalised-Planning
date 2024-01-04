from constants import TILE_WIDTH, TILE_HEIGHT
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

        tile_position = position.get("tile_position", None)
        pygame_position = position.get("pygame_position", None)
        tile = position.get("tile", None)

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

    def __eq__(self, other) -> bool:
        return self._tile_position == other.get_position()
