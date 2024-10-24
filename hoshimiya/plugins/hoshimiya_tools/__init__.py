from nonebot.plugin import PluginMetadata
from . import command as command

__plugin_meta__ = PluginMetadata(
    name="星泠工具库",
    description="什么都有喵",
    usage="#反馈 <消息内容>\n#头像 [ [cq:at] | <qquid> ]",
    supported_adapters={"OneBot V11"}
)

__all__ = []