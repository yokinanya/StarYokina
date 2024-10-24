from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.matcher import Matcher

from .model import CaveData

cave = on_fullmatch((".cave", "。cave"), ignorecase=True, permission=GROUP, block=True)


@cave.handle()
async def handle_cave(matcher: Matcher):
    cave_data = CaveData(category="default", caves=[]).get_random_cave()
    cave_image = (
        MessageSegment.image(file=f"{cave_data.image}")
        if cave_data.image is not None
        else ""
    )
    cave_title = f"{cave_data.title}\n" if cave_data.title is not None else ""
    message = f"回声洞 ({cave_data.id}) \n" + cave_title + cave_image
    await matcher.finish(message)


# jrdn = on_fullmatch("。jrdn", ignorecase=True, permission=GROUP, block=True)
