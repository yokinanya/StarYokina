from nonebot.plugin import PluginMetadata
from . import command as command
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="今日老婆",
    description="随机抽取群友作为老婆吧！",
    usage=(
        "指令表：\n"
        " 今日老婆\n"
        "   范围：群聊\n"
        "   介绍：随机抽取群友作为老婆，返回头像和昵称。当天已经抽取过回复相同老婆\n"
        " 换老婆\n"
        "   范围：群聊\n"
        "   介绍：重新抽取老婆\n"
        " #重置今日老婆\n"
        "   权限：su\n"
        "   范围：群聊\n"
        "   介绍：清空今日本群老婆数据\n"
        " #(开启/关闭)换老婆\n"
        "   权限：su/群主/管理员\n"
        "   范围：群聊\n"
        "   介绍：开启/关闭本群换老婆功能\n"
        " #设置换老婆次数 <N>\n"
        "   权限：su/群主/管理员\n"
        "   范围：群聊\n"
        "   介绍：设置本群换老婆最大次数\n"
        "   参数：\n"
        "     N：指定整数次数"
    ),
    supported_adapters={"OneBot V11"},
)
