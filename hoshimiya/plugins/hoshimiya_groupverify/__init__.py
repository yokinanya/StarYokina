from nonebot.plugin import PluginMetadata
from . import command as command

__plugin_meta__ = PluginMetadata(
    name="加群验证",
    description="",
    usage="#加群申请 -a 0 -r [reason] -f [事件编号]\n#加群管理 -s 0 -a 0 -p password",
    supported_adapters={"OneBot V11"}
)

__all__ = []