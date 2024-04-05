import configparser
from configparser import ConfigParser
from typing import Literal


class OptionManager(configparser.ConfigParser):

    def __init__(self, *, allow_no_value: Literal[True] = True):
        super().__init__(allow_no_value=allow_no_value)
        self.read("config.ini")

    def set_tile_size(self, size: int) -> None:
        self.set("DEFAULT", "tile_size", str(size))

    def get_tile_size(self) -> int:
        return self.getint("DEFAULT", "tile_size")
