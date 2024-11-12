import random
import time

from hoshimiya.utils.Onebotv11Utils import AtSB, download_avatar
from nonebot import get_driver, logger, on_command
from nonebot.adapters.onebot.v11 import Bot as Onebotv11Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters.onebot.v11.permission import GROUP, PRIVATE_FRIEND
from nonebot.matcher import Matcher
from nonebot.params import ArgStr, CommandArg
from nonebot.typing import T_State

from .config import hoshimiya_feedback_config
from .utils import ReverseGif, ReverseGifLock

superusers = get_driver().config.superusers
su = list(superusers)[0]

feedback_cooldown = hoshimiya_feedback_config.feedback_cooldown


LAST_SEND_TIME: int = 0

feedback = on_command(
    "feedback",
    aliases={"反馈"},
    permission=GROUP | PRIVATE_FRIEND,
    priority=20,
    block=True,
)


@feedback.handle()
async def handle_feedback(
    matcher: Matcher, state: T_State, cmd_arg: Message = CommandArg()
):
    now = int(time.time())
    if (now - LAST_SEND_TIME) < feedback_cooldown:
        await matcher.finish(
            f"该功能全局冷却中：剩余{feedback_cooldown - now + LAST_SEND_TIME}秒"
        )
    message = cmd_arg.extract_plain_text().strip()
    if message:
        state.update({"message": message})


@feedback.got("message", prompt="请输入需要发送的内容：")
async def handle_send_feedback(
    bot: Onebotv11Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    message: str = ArgStr("message"),
):
    global LAST_SEND_TIME
    qid = event.user_id
    base_message = f"收到来自{qid}的消息：\n"
    message = base_message + message.strip()
    await bot.send_private_msg(user_id=su, message=message)
    LAST_SEND_TIME = int(time.time())
    await matcher.finish("消息发送成功")


@on_command(
    "avatar", aliases={"头像"}, permission=GROUP, priority=20, block=True
).handle()
async def handle_download_avatar(
    matcher: Matcher,
    event: GroupMessageEvent,
    cmd_arg: Message = CommandArg(),
):
    message = cmd_arg.extract_plain_text().strip().split()
    sb = AtSB(event.model_dump_json())
    for item in message:
        if item.isdigit():
            sb.append(item)
    sb = list(map(lambda x: str(x), sb))
    sb = list(set(sb))
    if sb and "all" not in sb:
        for uin in sb:
            avatar = await download_avatar(uin)
            await matcher.send(f"已获取到{uin}的头像\n" + MessageSegment.image(avatar))
        if len(sb) > 3:
            await matcher.finish("已完成所有头像的获取")


@on_command(
    "reversegif",
    aliases={"倒放"},
    permission=GROUP,
    priority=20,
    block=True,
).handle()
async def handle_reverse_gif(
    matcher: Matcher,
    event: GroupMessageEvent,
    state: T_State,
) -> None:
    msg_images = None
    if ReverseGifLock.locker("status") is True:
        await matcher.finish("后台正在处理其他图像, 请稍后再试")
    # 首先处理消息中的图片
    if event.reply:
        original_message = event.reply.message
    else:
        original_message = event.message
    for seg in original_message:
        if seg.type == "image":
            msg_images = str(seg.data["url"]).replace("https://", "http://")

    if msg_images and not state.get("source_images"):
        state.update({"source_images": msg_images})
    source_images: str = state.get("source_images")

    # 没有获取到图像，请求输入
    if not source_images:
        await matcher.reject_arg("source_image", "请发送你想要倒放的GIF图片:")

    # 处理倒放
    try:
        await matcher.send("图像处理中，这可能需要几分钟")
        source_image = await ReverseGif(url=source_images)
        if not source_image is None:
            await matcher.send(MessageSegment.image(source_image))
        else:
            await matcher.send("传入图像过大，拒绝处理")
    except Exception as e:
        logger.error(f"ReverseGif | 图像处理失败, {e}")
        await matcher.finish("图像处理失败QAQ, 发生了意外的错误, 请稍后再试")


@on_command(
    cmd="rollone",
    permission=GROUP,
    priority=20,
    block=True,
).handle()
async def _(
    bot: Onebotv11Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    cmd_arg: Message = CommandArg(),
):
    all_member: list[dict] = await bot.get_group_member_list(group_id=event.group_id)
    roll_num = cmd_arg.extract_plain_text().strip()
    roll_num = int(roll_num) if roll_num.isdigit() else 1
    result = random.sample(all_member, roll_num)
    roll_result = ""
    for member in result:
        card = member["card"] if member["card"] is None else member["nickname"]
        uin = member["user_id"]
        roll_result += f"\n{card} ({uin})"
    await matcher.send(f"随机抽取{roll_num}人：\n" + roll_result)
