from hoshimiya.utils.Onebotv11Utils import download_avatar
from nonebot.adapters.onebot.v11 import Message, MessageSegment


async def construct_change_waifu_msg(
    member_info: dict,
    new_waifu_id: int,
    bot_id: int,
    times: int,
    limit_times: int,
    be_wiifu: bool,
) -> Message:
    if be_wiifu:
        return (
            MessageSegment.text(f"\n你今天已经被她娶走了哦~")
            + MessageSegment.image(img)
            + MessageSegment.text(
                f"{member_name}({new_waifu_id})\n乖乖的待在她身边不要乱跑哦~"
            )
        )
    if new_waifu_id == 0:
        return Message(f"\n渣男，你今天没老婆了！")
    member_name = member_info.get("card") or member_info.get("nickname") or new_waifu_id
    img = await download_avatar(str(new_waifu_id))
    if new_waifu_id == bot_id:
        return MessageSegment.text(
            f"\n你今天的群友老婆是我哦~"
            f"\n如果你这个渣男敢抛弃我的话，你今天就没老婆了哦"
        ) + MessageSegment.image(img)
    msg = MessageSegment.text("")
    if times == limit_times - 1:
        msg = MessageSegment.text(f"\n渣男，再换你今天就没老婆了！")
    return (
        msg
        + MessageSegment.text(f"\n你今天的群友老婆是：")
        + MessageSegment.image(img)
        + MessageSegment.text(f"{member_name}({new_waifu_id})")
    )


async def construct_waifu_msg(
    member_info: dict, waifu_id: int, bot_id: int, is_first: bool, be_wiifu: bool
) -> Message:
    """
    构造发送信息
    """
    if waifu_id == 0:
        return Message(f"\n渣男，你今天没老婆了！")
    member_name = member_info.get("card") or member_info.get("nickname") or waifu_id
    img = await download_avatar(str(waifu_id))
    if be_wiifu:
        return (
            MessageSegment.text(f"\n你今天已经被她娶走了哦~")
            + MessageSegment.image(img)
            + MessageSegment.text(
                f"{member_name}({waifu_id})\n乖乖的待在她身边不要乱跑哦~"
            )
        )
    if waifu_id == bot_id:
        if is_first:
            return MessageSegment.text(
                f"\n你今天的群友老婆是我哦~"
            ) + MessageSegment.image(img)
        else:
            return MessageSegment.text(
                f"\n你今天已经有老婆了，是我哦，不可以再有别人了呢~"
            ) + MessageSegment.image(img)

    if is_first:
        return (
            MessageSegment.text(f"\n你今天的群友老婆是：")
            + MessageSegment.image(img)
            + MessageSegment.text(f"{member_name}({waifu_id})")
        )
    return (
        MessageSegment.text(f"\n你今天已经有老婆了，要好好对待她哦~")
        + MessageSegment.image(img)
        + MessageSegment.text(f"{member_name}({waifu_id})")
    )
