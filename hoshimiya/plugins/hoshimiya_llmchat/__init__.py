from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.bot import Bot as Onebotv11Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.helpers import autorevoke_send
from nonebot.adapters.onebot.v11.message import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import driver

from .config import Config, plugin_config
from .utils import (GroupConfig, generate_forward_message,
                    generate_message_node, segment_message)

__plugin_meta__ = PluginMetadata(
    name="AI 群聊助手",
    description="基于 OpenAI 的群聊 AI 对话插件",
    usage="使用方法：\n1. 发送 '#ai <问题>' 进行 AI 对话\n2. 发送 '#ai 帮助' 查看帮助信息",
    type="application",
    homepage="https://github.com/yokinanya/StarYokina",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={"author": "yokinanya <yokinanya@ruau.top>"},
)


import base64
import httpx
from nonebot.adapters.onebot.v11 import MessageSegment
from .ai_chat import chat_with_ai

su: set = get_driver().config.superusers
nickname_set = get_driver().config.nickname
if nickname_set:
    # set 无序，取第一个元素
    nickname = next(iter(nickname_set))
else:
    nickname = "omega"


@driver.on_startup
async def startup() -> None:
    # 在启动时加载所有群的配置
    GroupConfig.load_from_file()


@on_command(("ai", "AI", "Ai"), priority=10, block=True).handle()
async def handle_ai_chat(bot: Onebotv11Bot, matcher: Matcher, event: GroupMessageEvent, cmd_arg: Message = CommandArg()):
    gconfig = GroupConfig(event.group_id)
    msg: Message = event.get_message()
    user_id = str(event.get_user_id())
    group_id = str(event.group_id)
    # 用 cmd_arg 获取原始消息文本用于管理命令判断
    user_prompt = cmd_arg.extract_plain_text().strip()
    # 优先处理管理命令和帮助命令
    if user_prompt in ["enable", "disable"]:
        if user_id not in su:
            await matcher.finish("你没有权限执行此命令")
        if user_prompt == "enable":
            gconfig.enable_openai()
            gconfig.save()
            await matcher.finish("AI 对话功能已启用")
        elif user_prompt == "disable":
            gconfig.disable_openai()
            gconfig.save()
            await matcher.finish("AI 对话功能已禁用")
        return
    if user_prompt == "帮助":
        help_text = (
            "AI 群聊助手使用指南：\n"
            "1. 发送 '#ai <问题>' 进行 AI 对话\n"
            "2. 每人每天可使用 AI 对话 {limit} 次\n"
            "3. 示例：#ai 介绍一下自己"
        ).format(limit=plugin_config.llmchat_daily_limit)
        await matcher.finish(help_text)
        return

    # 支持从回复消息中提取文本和图片
    reply_msg = event.reply.message if getattr(event, "reply", None) else None
    all_segments = list(msg)
    if reply_msg:
        all_segments += [
            seg for seg in reply_msg if seg.type in ("text", "image")]
    # 拼接文本时去除命令前缀（如 #ai、ai、/ai 等），只保留用户实际问题

    def strip_cmd_prefix(text: str) -> str:
        t = text.lstrip()
        lowers = t.lower()
        for prefix in ["#ai ", "/ai ", "ai ", "#ai", "/ai", "ai"]:
            if lowers.startswith(prefix):
                return t[len(prefix):].lstrip()
        return t
    user_prompt = "".join(strip_cmd_prefix(seg.data.get("text", "")) if i == 0 else seg.data.get("text", "")
                          for i, seg in enumerate(all_segments) if seg.type == "text").strip()

    # 重新加载内存状态，确保开关变更后立即生效
    gconfig.load_from_ram()
    if not gconfig.openai_enabled:
        await matcher.finish("AI 对话功能未启用，请联系管理员设置")

    # 检查文本有效性
    if not user_prompt and not any(seg.type == "image" for seg in all_segments):
        await matcher.finish("请输入有效的问题，例如：#ai 今天天气怎么样？")
        return

    # 组装 multimodal content（文本+图片），支持回复消息
    multimodal_content = []
    if user_prompt:
        multimodal_content.append({"type": "text", "text": user_prompt})
    for seg in all_segments:
        if seg.type != "image":
            continue
        url = seg.data.get("url")
        if not url:
            continue
        url = url.replace("https://", "http://")
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    img_bytes = resp.content
                    # 自动识别 mime 类型
                    ext = url.lower().rsplit('.', 1)[-1]
                    if ext == "png":
                        mime = "image/png"
                    elif ext == "gif":
                        mime = "image/gif"
                    elif ext == "bmp":
                        mime = "image/bmp"
                    elif ext == "webp":
                        mime = "image/webp"
                    else:
                        mime = "image/jpeg"
                    img_b64 = base64.b64encode(img_bytes).decode()
                    multimodal_content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{img_b64}"}
                    })
        except Exception:
            pass

    from .utils import ai_chat_acquire, ai_chat_release
    try:
        await ai_chat_acquire()
    except RuntimeError as e:
        await matcher.finish(str(e))
        return
    try:
        await autorevoke_send(bot=bot, event=event, message="正在思考中...", revoke_interval=30)
        response = await chat_with_ai(multimodal_content, user_id)
        segment_messages = segment_message(response)
        messages = [generate_message_node(
            bot.self_id, nickname, [segment]) for segment in segment_messages]
        forward_data = generate_forward_message(group_id, messages)
        await bot.call_api(
            "send_forward_msg",
            message_type="group",
            group_id=event.group_id,
            messages=forward_data["messages"]
        )
    finally:
        ai_chat_release()
