from nonebot import get_plugin_config
from pydantic import BaseModel


class HoshiMiyaFeedback(BaseModel):
    feedback_cooldown: int = 120

    class Config:
        extra = "ignore"


hoshimiya_feedback_config = get_plugin_config(HoshiMiyaFeedback)

__all__ = ["hoshimiya_feedback_config"]
