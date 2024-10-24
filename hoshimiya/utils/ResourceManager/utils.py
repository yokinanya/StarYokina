import os
import pathlib
import sys

LOCAL_RESOURCE_DIR = (
    pathlib.Path(os.path.abspath(sys.path[0]))
    .joinpath("hoshimiya")
    .joinpath("resource")
)
if not os.path.exists(LOCAL_RESOURCE_DIR):
    os.makedirs(LOCAL_RESOURCE_DIR)


class Resource:
    def __init__(self, module: pathlib.Path) -> None:
        self.module = module

        if not os.path.exists(LOCAL_RESOURCE_DIR.joinpath(self.module)):
            os.makedirs(LOCAL_RESOURCE_DIR.joinpath(self.module))

    def datapath(self) -> pathlib.Path:
        return LOCAL_RESOURCE_DIR.joinpath(self.module)
