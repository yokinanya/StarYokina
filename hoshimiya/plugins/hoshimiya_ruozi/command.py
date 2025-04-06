import httpx
from nonebot import on_regex
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.matcher import Matcher


@on_regex(
    pattern="^(.|。)(弱智|ruozi|rzb)$",
    permission=GROUP,
    priority=20,
    block=True,
).handle()
async def handle_ruozi(matcher: Matcher):
    async with httpx.AsyncClient() as client:
        response = await client.get(url="https://api.7ed.net/ruozi/api")
        data = response.json()
    try:
        await matcher.finish(data["ruozi"])
    except KeyError:
        await matcher.finish("消息获取失败")
