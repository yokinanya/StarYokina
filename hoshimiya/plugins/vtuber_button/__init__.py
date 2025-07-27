from nonebot.plugin import PluginMetadata


__plugin_meta__ = PluginMetadata(
    name="猫按钮",
    description="【猫按钮插件】\n" "发出可爱的猫叫",
    usage="@bot 喵一个",
    supported_adapters={"OneBot V11"}
)

from . import command as command

__all__ = []