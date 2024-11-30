import httpx
from nonebot import on_command
from nonebot.adapters.onebot.v11.bot import Bot as OneBotv11
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from .utils import areaNametoAreaId, readData, startLive, stopLive, changeLiveTitle

cookies = httpx.Cookies()


async def setup_cookies(uin):
    data = await readData(uin)
    if not data:
        raise ValueError("找不到对应的直播间")

    cookies.set("SESSDATA", data["cookies"]["SESSDATA"], domain=".bilibili.com")
    cookies.set("bili_jct", data["cookies"]["bili_jct"], domain=".bilibili.com")
    return data["room_id"]


@on_command(
    "startlive",
    aliases={"开播"},
    permission=SUPERUSER,
    priority=5,
    block=True,
).handle()
async def startlive(
    bot: OneBotv11,
    event: MessageEvent,
    matcher: Matcher,
    cmd_arg: Message = CommandArg(),
):
    try:
        uin = event.user_id
        room_id = await setup_cookies(uin)

        area = cmd_arg.extract_plain_text().strip() or "745"
        area_id = await areaNametoAreaId(area)

        msg = await startLive(room_id=room_id, area_v2=area_id, cookies=cookies)
        await matcher.finish(msg)
    except ValueError as e:
        await matcher.finish(f"操作失败，{e}")


@on_command(
    "stoplive",
    aliases={"下播"},
    permission=SUPERUSER,
    priority=5,
    block=True,
).handle()
async def stoplive(
    event: MessageEvent,
    matcher: Matcher,
):
    try:
        uin = event.user_id
        room_id = await setup_cookies(uin)

        msg = await stopLive(room_id=room_id, cookies=cookies)
        await matcher.finish(msg)
    except ValueError as e:
        await matcher.finish(f"操作失败，{e}")


@on_command(
    "changetitle",
    aliases={"直播间标题"},
    permission=SUPERUSER,
    priority=5,
    block=True,
).handle()
async def changetitle(
    event: MessageEvent,
    matcher: Matcher,
    cmd_arg: Message = CommandArg(),
):
    try:
        uin = event.user_id
        room_id = await setup_cookies(uin)

        title = cmd_arg.extract_plain_text().strip() or "测试喵"
        msg = await changeLiveTitle(room_id=room_id, title=title, cookies=cookies)
        await matcher.finish(msg)
    except ValueError as e:
        await matcher.finish(f"操作失败，{e}")
