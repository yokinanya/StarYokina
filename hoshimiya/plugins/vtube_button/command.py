import re
from pathlib import Path
from nonebot.log import logger
from nonebot.plugin import on_command, on_regex, PluginMetadata
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP, GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.params import CommandArg, ArgStr, EventMessage

from .utils import (
    get_voice_resource,
    get_available_voice_resource,
    get_voice_resource_name,
    set_voice_resource,
    get_group_status,
    set_group_status,
)

__plugin_meta__ = PluginMetadata(
    name="猫按钮",
    description="【猫按钮插件】\n" "发出可爱的猫叫",
    usage="@bot 喵一个",
    extra={"author": "Ailitonia"},
)

button_pattern = r"^(.*?)喵一个$"


@on_regex(
    button_pattern,
    rule=to_me(),
    permission=GROUP,
    priority=50,
    block=False,
).handle()
async def handle_miya_button(
    bot: Bot,
    event: GroupMessageEvent,
    matcher: Matcher,
    message: Message = EventMessage(),
):
    if get_group_status(bot, event, matcher) is False:
        await matcher.finish()
    message = message.extract_plain_text().strip()
    search_result = re.search(button_pattern, message)
    keyword = search_result.group(1)
    keyword = keyword if keyword else None
    resource_name = await get_voice_resource_name(bot=bot, event=event, matcher=matcher)
    voice_resource = get_voice_resource(resource_name=resource_name)
    voice_file = voice_resource.get_random_voice()
    voice_msg = MessageSegment.record(file=voice_file)
    try:
        await matcher.finish(voice_msg)
    except ActionFailed:
        voice_path = voice_file.replace(r"/home/ubuntu/nonebot/omega-miya/hoshimiya/plugins/vtube_button/voices/","")
        await matcher.finish(f"出现错误：{voice_path}")



set_resource = on_command(
    "SetButtonVoiceResource",
    aliases={"设置猫按钮语音"},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=20,
    block=True,
)


@set_resource.handle()
async def handle_parse_resource_name(
    state: T_State, matcher: Matcher, cmd_arg: Message = CommandArg()
):
    """首次运行时解析命令参数"""
    resource_name = cmd_arg.extract_plain_text().strip()
    if resource_name:
        state.update({"resource_name": resource_name})
    else:
        resource_msg = "\n".join(get_available_voice_resource())
        await matcher.send(f"当前可用的猫按钮语音有:\n\n{resource_msg}")


@set_resource.got("resource_name", prompt="请输入想要配置的猫按钮语音名称:")
async def handle_delete_user_sub(
    bot: Bot,
    event: GroupMessageEvent,
    matcher: Matcher,
    resource_name: str = ArgStr("resource_name"),
):
    resource_name = resource_name.strip()
    if resource_name not in get_available_voice_resource():
        await matcher.reject(f"{resource_name}不是可用的猫按钮语音, 重新输入:")

    setting_result = await set_voice_resource(
        resource_name=resource_name, bot=bot, event=event, matcher=matcher
    )
    if isinstance(setting_result, Exception):
        logger.error(f"SetButtonVoiceResource | 配置猫按钮语音失败, {setting_result}")
        await matcher.finish(f"设置猫按钮语音失败了QAQ, 请稍后重试或联系管理员处理")
    else:
        logger.success(f"SetButtonVoiceResource | 配置猫按钮语音成功")
        await matcher.finish(f"已将猫按钮语音设置为: {resource_name}")


set_status = on_command(
    "DisableButtonVoice",
    aliases={"关闭猫按钮"},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=20,
    block=True,
).handle()


async def handle_miya_button(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    if set_group_status(False) is True:
        await matcher.finish(f"已关闭本群猫按钮")
    else:
        await matcher.finish(f"关闭本群猫按钮失败")


__all__ = []
