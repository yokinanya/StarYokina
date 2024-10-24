import os
import sys
from pathlib import Path

DEFULT_DIRECTORY = (
    Path(os.path.abspath(sys.path[0])).joinpath("hoshimiya").joinpath("data")
)


class DatabaseConfig:

    def __init__(self, directory: Path = DEFULT_DIRECTORY):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
