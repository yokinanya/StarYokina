from nonebot import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from .model import Voice, Resources
from .vtb_voice import miya_voices, mnk_voices, taffy_voices, ayame_voices


_DEFAULT_VOICE_RESOURCE: Voice = miya_voices
"""默认的按钮资源"""
_INTERNAL_VOICE_RESOURCE: dict[str, Voice] = {
    "Miya按钮": miya_voices,
    "MNK按钮": mnk_voices,
    "塔菲按钮": taffy_voices,
    "余按钮": ayame_voices,
}


def get_voice_resource(resource_name: str | None = None) -> Voice:
    if resource_name is None:
        return _DEFAULT_VOICE_RESOURCE
    return _INTERNAL_VOICE_RESOURCE.get(resource_name, _DEFAULT_VOICE_RESOURCE)


def get_available_voice_resource() -> list[str]:
    return [x for x in _INTERNAL_VOICE_RESOURCE.keys()]


async def _get_voice_resource_name(
    bot: Bot, event: GroupMessageEvent, matcher: Matcher
) -> str | None:
    """根据当前 event 获取对应按钮资源名"""
    groupid = str(event.group_id)
    r = Resources()
    try:
        if r.isEnabled(groupid) is True:
            return r.getResource(groupid)
    except KeyError:
        r.updateData(groupid)
        return None


async def get_voice_resource_name(
    bot: Bot, event: GroupMessageEvent, matcher: Matcher
) -> str | None:
    """根据当前 event 获取对应对象按钮资源名"""
    result = await _get_voice_resource_name(bot=bot, event=event, matcher=matcher)
    if isinstance(result, Exception):
        result = None
    return result


async def set_voice_resource(
    resource_name: str, bot: Bot, event: GroupMessageEvent, matcher: Matcher
) -> bool:
    """根据当前 event 配置对应对象按钮资源"""
    groupid = str(event.group_id)
    r = Resources()
    try:
        r.updateData(groupid, True, resource_name)
        return True
    except Exception as e:
        logger.exception(e)
        return False


async def get_group_status(
    bot: Bot, event: GroupMessageEvent, matcher: Matcher
) -> bool:
    groupid = str(event.group_id)
    r = Resources()
    try:
        status = r.isEnabled(groupid)
    except KeyError:
        r.updateData(groupid)
        status = False
    return status


async def set_group_status(
    enable_value: bool, bot: Bot, event: GroupMessageEvent, matcher: Matcher
) -> bool:
    """根据当前 event 配置对应对象按钮资源"""
    groupid = str(event.group_id)
    r = Resources()
    try:
        r.updateData(groupid, enable_value)
        return True
    except Exception as e:
        logger.exception(e)
        return False


__all__ = [
    "get_voice_resource",
    "get_available_voice_resource",
    "get_voice_resource_name",
    "set_voice_resource",
    "get_group_status",
]
