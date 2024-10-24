from nonebot import get_plugin_config
from pydantic import BaseModel


class QQManagerConfig(BaseModel):
    callback_notice: bool = True  # 是否在操作完成后在 QQ 返回提示
    ban_rand_time_min: int = 60  # 随机禁言最短时间(s) default: 1分钟
    ban_rand_time_max: int = 2591999  # 随机禁言最长时间(s) default: 30天: 60*60*24*30

    class Config:
        extra = "ignore"

qqmanager_plugin_config = get_plugin_config(QQManagerConfig)

__all__ = [
    'qqmanager_plugin_config'
]