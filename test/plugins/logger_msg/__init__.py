from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import MessageEvent as OneBotV11MessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP


@on_command(("debug", "logger"), permission=GROUP, priority=20, block=False).handle()
async def _(event: OneBotV11MessageEvent):
    if event.reply:
        original_reply_message = event.reply.message
        logger.info(original_reply_message)
        for seg in original_reply_message:
            logger.info(seg)
