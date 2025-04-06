import datetime
import random

from nonebot import get_driver, on_command, on_regex
from nonebot.adapters.onebot.v11 import Message
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

    gconfig = wifeSettings(gid)
    gconfig.getConfig()

    # 初始化变量
    is_first = False
    be_wife = False
    wife_id = 0
    today = str(datetime.date.today())

    grecord = wifeRecord(gid, qid, date=today)
    grecord.check_date()
    bewife_id = grecord.get_bewife()
    _wife_id = grecord.get_wife()

    if bewife_id:
        is_first = False
        be_wife = True
        wife_id = bewife_id
    elif _wife_id is not None:  # 修正判断逻辑
        is_first = False
        be_wife = False
        wife_id = _wife_id
    else:
        try:
            all_member = await bot.get_group_member_list(group_id=gid)
            # 使用生成器优化集合操作
            existed_wives = set(grecord.get_allwife())
            id_set = set(m["user_id"] for m in all_member) - existed_wives - ban_id
            id_set.discard(int(qid))

            wife_id = random.choice(list(id_set)) if id_set else int(bot.self_id)
        except Exception as e:
            wife_id = int(bot.self_id)
            is_first = False
            be_wife = False
        else:
            is_first = True
            be_wife = False
            grecord.wife_id = wife_id
            grecord.times = 0

    if not be_wife:
        grecord.save()

    try:
        member_info = await bot.get_group_member_info(
            group_id=int(gid), user_id=wife_id
        )
    except ActionFailed:
        member_info = {}
    except Exception as e:
        member_info = {}

    try:
        message: Message = await construct_waifu_msg(
            member_info, wife_id, int(bot.self_id), is_first, be_wife
        )
    except Exception as e:
        message = Message("老婆信息生成失败，请稍后再试")

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
    gconfig = wifeSettings(gid)
    gconfig.getConfig()
    limit_times = gconfig.limit_times
    allow_change_waifu = gconfig.allow_change_wife
    bot_id = int(bot.self_id)  # 预计算机器人ID

    # 情人节禁止更换
    if datetime.date.today().strftime("%m%d") == "0214":
        allow_change_waifu = False

    be_waifu = False  # 修正变量名拼写
    today = str(datetime.date.today())
    grecord = wifeRecord(gid, qid, date=today)
    grecord.check_date()

    if (wife_id := grecord.get_wife()) is None:
        await matcher.finish("换老婆前请先娶个老婆哦，渣男", at_sender=True)
    if not allow_change_waifu:
        await matcher.finish(
            "你今天已经有老婆了，还想娶小妾啊？爪巴，花心大萝卜", at_sender=True
        )

    old_times = grecord.times
    if bewife_id := grecord.get_bewife():
        new_waifu_id = bewife_id
        be_waifu = True
    elif old_times >= limit_times or wife_id == bot_id:
        new_waifu_id = 0
        old_times = limit_times
    else:
        # 优化集合操作
        members = await bot.get_group_member_list(group_id=int(gid))
        exist_wives = set(grecord.get_allwife()) | {int(qid), wife_id, bot_id}
        available_ids = (
            {m["user_id"] for m in members}
            - exist_wives
            - (ban_id if isinstance(ban_id, set) else set())
        )

        new_waifu_id = random.choice(list(available_ids)) if available_ids else bot_id

    # 处理特殊ID情况
    if new_waifu_id == 0:
        member_info = {}
    else:
        try:
            member_info = await bot.get_group_member_info(
                group_id=int(gid), user_id=new_waifu_id
            )
        except Exception:  # 扩展异常捕获范围
            member_info = {}

    # 更新记录
    grecord.wife_id = new_waifu_id
    grecord.times += 1
    if not be_waifu:
        grecord.save()

    message: Message = await construct_change_waifu_msg(
        member_info, new_waifu_id, bot_id, old_times, limit_times, be_waifu
    )
    await matcher.finish(message, at_sender=True)
