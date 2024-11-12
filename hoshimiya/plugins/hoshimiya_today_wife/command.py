import datetime
import random

from nonebot import get_driver, on_command, on_regex
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11 import GROUP, ActionFailed
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RawCommand
from nonebot.permission import SUPERUSER

from .config import wife_config
from .model import wifeRecord, wifeSettings
from .uitls import construct_change_waifu_msg, construct_waifu_msg

driver = get_driver()

ban_id = wife_config.today_waifu_ban_id_list


@driver.on_startup
def init_plugin() -> None:
    wifeSettings(gid=0).initConfig()


# 设置所在群换老婆最大次数
@on_command(
    cmd="设置换老婆次数",
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN,
    priority=20,
    block=True,
).handle()
async def _(
    matcher: Matcher, event: GroupMessageEvent, cmd_arg: Message = CommandArg()
):
    limit_times = cmd_arg.extract_plain_text().strip()
    gid = str(event.group_id)
    gconfig = wifeSettings(gid)
    if limit_times.isdigit():
        gconfig.limit_times = int(limit_times)
        gconfig.updateConfig()
        await matcher.finish(f"已将本群换老婆次数设置为{limit_times}次")
    else:
        await matcher.finish("未提供设置次数, 已取消操作")


@on_command(
    cmd="开启换老婆",
    aliases={"关闭换老婆"},
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN,
    priority=20,
    block=True,
).handle()
async def _(matcher: Matcher, event: GroupMessageEvent, cmd: Message = RawCommand()):
    gid = str(event.group_id)
    gconfig = wifeSettings(gid)
    cmd = str(cmd).replace("#", "")
    if cmd == "开启换老婆":
        gconfig.allow_change_wife = True
    elif cmd == "关闭换老婆":
        gconfig.allow_change_wife = False
    else:
        await matcher.finish()
    await matcher.finish(f"本群设置为{cmd}")


@on_command(
    cmd="重置今日老婆",
    permission=SUPERUSER,
    priority=20,
    block=True,
).handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    gid = str(event.group_id)
    qid = str(event.user_id)
    today = str(datetime.date.today())
    grecord = wifeRecord(gid, qid, date=today)
    grecord.reset()
    await matcher.finish("今日老婆已刷新！")


@on_regex(
    pattern="^今日老婆$",
    permission=GROUP,
    priority=20,
    block=True,
).handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    gid = str(event.group_id)
    qid = str(event.user_id)
    if qid in ["1099332511", "3872394754"]:
        await matcher.finish("你已经有老婆了，要好好对待她哦~", at_sender=True)

    gconfig = wifeSettings(gid)
    gconfig.getConfig()
    is_first: bool  # 是否已经存在老婆标记
    wife_id: int  # 老婆id
    today = str(datetime.date.today())

    grecord = wifeRecord(gid, qid, date=today)
    # 如果不存在今天的记录，清空本群记录字典，并添加今天的记录，保存标记置为真
    grecord.check_date()
    bewife_id = grecord.get_bewife()
    _wife_id = grecord.get_wife()
    if bewife_id:
        # 如果用户已经是群友的老婆
        is_first = False
        be_wiifu = True
        wife_id = bewife_id
    elif _wife_id or _wife_id == 0:
        # 如果用户已经有老婆记录
        is_first = False
        be_wiifu = False
        wife_id = _wife_id
    else:
        # 如果用户在今天无老婆记录，随机从群友中抓取一位作为老婆
        all_member = await bot.get_group_member_list(group_id=gid)
        id_set = (
            set(i["user_id"] for i in all_member)
            - set(i for i in grecord.get_allwife())
            - ban_id
        )
        id_set.discard(int(qid))
        if id_set:
            wife_id: int = random.choice(list(id_set))
        else:
            # 如果剩余群员列表为空，默认机器人作为老婆
            wife_id: int = int(bot.self_id)

        is_first = True
        be_wiifu = False
        grecord.wife_id = wife_id
        grecord.times = 0

    grecord.save()

    try:
        member_info = await bot.get_group_member_info(
            group_id=int(gid), user_id=wife_id
        )
    except ActionFailed:
        # 群员已经退群情况
        member_info = {}
    message: Message = await construct_waifu_msg(
        member_info, wife_id, int(bot.self_id), is_first, be_wiifu
    )
    await matcher.finish(message, at_sender=True)


@on_regex(
    pattern="^换老婆$",
    permission=GROUP | SUPERUSER,
    priority=20,
    block=True,
).handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    gid = str(event.group_id)
    qid = str(event.user_id)
    if qid in ["1099332511", "3872394754"]:
        await matcher.finish("你已经有老婆了，要好好对待她哦~", at_sender=True)
    gconfig = wifeSettings(gid)
    gconfig.getConfig()
    limit_times = gconfig.limit_times
    allow_change_waifu = gconfig.allow_change_wife

    be_wiifu = False
    today = str(datetime.date.today())
    grecord = wifeRecord(gid, qid, date=today)
    # 如果不存在今天的记录，清空本群记录字典，并添加今天的记录，保存标记置为真
    grecord.check_date()

    if grecord.get_bewife():
        # 如果用户已经是群友的老婆
        new_waifu_id = grecord.get_bewife()
        be_wiifu = True
    elif grecord.get_wife() is None:
        await matcher.finish("换老婆前请先娶个老婆哦，渣男", at_sender=True)
    if not allow_change_waifu:
        await matcher.finish("请专一的对待自己的老婆哦", at_sender=True)

    old_waifu_id = grecord.get_wife()
    old_times = grecord.times
    if old_times >= limit_times or old_waifu_id == int(bot.self_id):
        new_waifu_id = 0
        old_times = limit_times
    else:
        all_member: list = await bot.get_group_member_list(group_id=gid)
        id_set = (
            set(i["user_id"] for i in all_member)
            - set(i for i in grecord.get_allwife())
            - ban_id
        )
        id_set.discard(int(qid))
        id_set.discard(old_waifu_id)
        if id_set:
            new_waifu_id: int = random.choice(list(id_set))
        else:
            # 如果剩余群员列表为空，默认机器人作为老婆
            new_waifu_id: int = int(bot.self_id)

    grecord.wife_id = new_waifu_id
    grecord.times = grecord.times + 1
    grecord.save()

    try:
        member_info = await bot.get_group_member_info(
            group_id=int(gid), user_id=new_waifu_id
        )
    except ActionFailed:
        # 群员已经退群情况
        member_info = {}
    message: Message = await construct_change_waifu_msg(
        member_info, new_waifu_id, int(bot.self_id), old_times, limit_times, be_wiifu
    )
    await matcher.finish(message, at_sender=True)
