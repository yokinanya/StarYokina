from hoshimiya.utils.Onebotv11Utils.utils import (
    LOCAL_TMP_DIR,
    OMEGA_LOCAL_TMP_DIR,
)
from hoshimiya.utils.Onebotv11Utils import convert_size
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

from .utils import BotTempManager


@on_command(
    "temp",
    aliases={"缓存", "tmp"},
    priority=20,
    block=True,
    rule=to_me(),
    permission=SUPERUSER,
).handle()
async def handle_temp(matcher: Matcher):
    OmegaMiyaTMP = BotTempManager().get_size(OMEGA_LOCAL_TMP_DIR)
    HoshiMiyaTMP = BotTempManager().get_size(LOCAL_TMP_DIR)
    await matcher.send(
        f"缓存大小 (包含持久化存储)：\nOmegaMiya\t-\t{convert_size(OmegaMiyaTMP)}\nHoshiMiya\t-\t{convert_size(HoshiMiyaTMP)}"
    )


@on_command(
    "autoclean",
    aliases={"缓存清理"},
    priority=20,
    block=True,
    rule=to_me(),
    permission=SUPERUSER,
).handle()
async def handle_temp(matcher: Matcher):
    await BotTempManager().delete(OMEGA_LOCAL_TMP_DIR)
    await BotTempManager().delete(LOCAL_TMP_DIR)
    await matcher.send("已清除缓存")
