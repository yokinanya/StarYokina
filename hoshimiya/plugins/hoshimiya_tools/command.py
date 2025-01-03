import time
import httpx

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
        remaining_time = feedback_cooldown - (now - LAST_SEND_TIME)
        await matcher.finish(f"该功能全局冷却中：剩余{remaining_time}秒")

    message = cmd_arg.extract_plain_text().strip()
    if message:
        state["message"] = message


@feedback.got("message", prompt="请输入需要发送的内容：")
async def handle_send_feedback(
    bot: Onebotv11Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    message: str = ArgStr("message"),
):
    global LAST_SEND_TIME
    qid = event.user_id
    message_content = f"收到来自{qid}的消息：\n{message.strip()}"

    try:
        await bot.send_private_msg(user_id=su, message=message_content)
        LAST_SEND_TIME = int(time.time())
        await matcher.finish("消息发送成功")
    except Exception:
        await matcher.finish("消息发送失败，请稍后再试。")


@on_command(
    "avatar", aliases={"头像"}, permission=GROUP, priority=20, block=True
).handle()
async def handle_download_avatar(
    matcher: Matcher, event: GroupMessageEvent, cmd_arg: Message = CommandArg()
):
    message = cmd_arg.extract_plain_text().strip().split()
    sb = AtSB(event.model_dump_json())
    sb.extend(item for item in message if item.isdigit())
    sb = list(set(map(str, sb)))

    if sb and "all" not in sb:
        for uin in sb:
            avatar = await download_avatar(uin)
            await matcher.send(f"已获取到{uin}的头像\n" + MessageSegment.image(avatar))
        if len(sb) > 3:
            await matcher.finish("已完成所有头像的获取")


@on_command(
    "reversegif", aliases={"倒放"}, permission=GROUP, priority=20, block=True
).handle()
async def handle_reverse_gif(matcher: Matcher, event: GroupMessageEvent) -> None:
    if ReverseGifLock.locker("status"):
        await matcher.finish("后台正在处理其他图像, 请稍后再试")

    original_message = event.reply.message if event.reply else event.message
    msg_images = next(
        (
            str(seg.data["url"]).replace("https://", "http://")
            for seg in original_message
            if seg.type == "image"
        ),
        None,
    )

    if not msg_images:
        await matcher.reject("请发送你想要倒放的GIF图片:")

    await matcher.send("图像处理中，这可能需要几分钟")

    try:
        source_image = await ReverseGif(url=msg_images)
        if source_image:
            await matcher.send(MessageSegment.image(source_image))
        else:
            await matcher.send("传入图像过大，拒绝处理")
    except Exception as e:
        logger.error(f"ReverseGif | 图像处理失败, {e}")
        await matcher.finish("图像处理失败QAQ, 发生了意外的错误, 请稍后再试")


@on_command(
    cmd="save", aliases={"保存"}, permission=GROUP, priority=20, block=True
).handle()
async def handle_save(matcher: Matcher, event: GroupMessageEvent):
    original_message = event.reply.message if event.reply else event.message
    strick_url = next(
        (
            str(seg.data["url"]).replace("https://", "http://")
            for seg in original_message
            if seg.type == "image"
        ),
        None,
    )

    if not strick_url:
        await matcher.reject("请发送你想要保存的表情:")

    if "gxh.vip.qq.com" in strick_url:
        strick_url_png = strick_url.replace("raw300.gif", "300x300.png")
        http_code = httpx.get(strick_url_png).status_code
        if http_code not in [400, 599]:
            strick_url = strick_url_png

    content = MessageSegment.image(strick_url, type_=0)
    await matcher.send(content + "原始链接：" + strick_url)
