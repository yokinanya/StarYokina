from nonebot import get_plugin_config
from pydantic import BaseModel
from typing import Literal


class HoshiMiyaFeedback(BaseModel):
    notice_group_mode: Literal["whitelist", "blacklist"] = "whitelist"
    notice_group_whitelist: list[int] = []
    notice_group_blacklist: list[int] = []
    feedback_cooldown: int = 120

    class Config:
        extra = "ignore"


hoshimiya_feedback_config = get_plugin_config(HoshiMiyaFeedback)

__all__ = ["hoshimiya_feedback_config"]
