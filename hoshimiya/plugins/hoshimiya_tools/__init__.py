from nonebot.plugin import PluginMetadata
from . import command as command

__plugin_meta__ = PluginMetadata(
    name="星泠工具库",
    description="什么都有喵\n\n已知Bug: \n - 保存表情功能不支持原创表情，但可以把原创表情转换为支持倒放的格式",
    usage="#反馈 <消息内容>\n#头像 [ [cq:at] | <qquid> ]\n#倒放 <gif图片>\n#保存 <表情图片>",
    supported_adapters={"OneBot V11"}
)

__all__ = []