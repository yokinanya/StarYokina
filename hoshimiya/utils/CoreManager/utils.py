import os
import sys
from pathlib import Path
from typing import Literal, Optional

from nonebot import logger

from .error import *

LOCAL_LOCK_DIR = (
    Path(os.path.abspath(sys.path[0])).joinpath("hoshimiya").joinpath(".lock")
)
if not os.path.exists(LOCAL_LOCK_DIR):
    os.makedirs(LOCAL_LOCK_DIR)


class PluginBase:
    def __init__(self, name):
        self.name: str = name


class PluginLock(PluginBase):
    def __init__(self, name):
        super().__init__(name)
        self.status: bool

    def locker(self, mode: Literal["lock", "unlock", "status"]) -> Optional[bool]:
        lockfile = LOCAL_LOCK_DIR.joinpath(f"{self.name}.lock")

        self.status = os.path.exists(lockfile)

        match mode:
            case "lock":
                if self.status is True:
                    raise LockExist
                with open(lockfile, "w"):
                    pass
            case "unlock":
                if self.status is True:
                    os.remove(lockfile)
            case "status":
                return self.status

class BotSettings:
    def __init__(self) -> None:
        pass

class BotTempManager:
    async def _delete_file(self, file_path) -> None:
        try:
            os.remove(file_path)
            logger.debug(f"Deleted: {file_path}")
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting {file_path}: {e}")

    async def delete(self, directory: Optional[str | Path]) -> None:
        blacklist = ["message_transfer_utils"]
        for entry in os.scandir(directory):
            if entry.is_file():
                await self._delete_file(entry.path)
            elif entry.is_dir() and entry.name not in blacklist:
                await self.delete(entry.path)

    def get_size(self, directory: Optional[str | Path]) -> int:
        total_size = 0
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += self.get_size(entry.path)  # 递归计算子目录大小
        return total_size


all = ["PluginBase", "PluginLock", "BotTempManager"]
