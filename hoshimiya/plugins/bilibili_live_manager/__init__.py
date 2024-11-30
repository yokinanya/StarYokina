from nonebot.plugin import PluginMetadata
from . import command as command

__plugin_meta__ = PluginMetadata(
    name="哔哩哔哩直播间管理",
    description="快速开播，绕过分区限制开播，需手动录入账号信息",
    usage="#开播 [分区]\n#下播\n#直播间标题 [标题]\n",
    supported_adapters={"OneBot V11"},
)

__all__ = []
