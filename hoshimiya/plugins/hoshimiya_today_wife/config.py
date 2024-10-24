from pathlib import Path
from typing import List, Set

from nonebot import get_plugin_config
from pydantic import BaseModel, field_validator


class Config(BaseModel):
    today_waifu_ban_id_list: Set[int] = set()
    today_waifu_default_change_waifu: bool = True
    today_waifu_default_limit_times: int = 2


    @field_validator('today_waifu_ban_id_list')
    def check_ban_id(cls, v: List[int]) -> Set[int]:
        if not (isinstance(v, list) or isinstance(v, set)):
            return set()
        return set(map(int, v))

    class Config:
        extra = "ignore"

wife_config = get_plugin_config(Config)

__all__ = [
    'wife_config'
]