import configparser
from typing import Literal
from functools import wraps


class OptionManager(configparser.ConfigParser):

    def __init__(self, *, allow_no_value: Literal[True] = True):
        super().__init__(allow_no_value=allow_no_value)
        self._config_file = 'config.ini'
        self.read(self._config_file)

    @staticmethod
    def setter(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            function(self, *args, **kwargs)
            with open(self._config_file, 'w') as config_file:
                self.write(config_file)

        return wrapper

    @setter
    def set_tile_size(self, size: int) -> None:
        default_screen_length = self.getint("Default", "screen_length")
        screen_length = default_screen_length + (default_screen_length % size)
        self.set("Runtime", "screen_length", str(screen_length))
        self.set("Runtime", "tile_size", str(size))

    def get_tile_size(self) -> int:
        return self.getint("Runtime", "tile_size")

    def get_screen_length(self) -> int:
        return self.getint("Runtime", "screen_length")
