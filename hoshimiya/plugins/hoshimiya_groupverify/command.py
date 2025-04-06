import re
from typing import Annotated

from nonebot import on_request, on_shell_command, on_startswith
from nonebot.adapters.onebot.v11 import (
    GROUP_ADMIN,
    GROUP_OWNER,
    Bot,
    GroupMessageEvent,
    GroupRequestEvent,
)
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.rule import ArgumentParser, Namespace
from nonebot.typing import T_Handler
from pydantic import BaseModel

from .model import GroupVerifyConfig


@on_request().handle()
async def handle_group_request(bot: Bot, event: GroupRequestEvent, matcher: Matcher):
    try:
        # 预编译正则表达式提升匹配效率
        ANSWER_PATTERN = re.compile(r"答案：(.*)")
        # 显式处理None值
        comment = event.comment or ""
        gid = event.group_id
        uid = event.user_id
        sub_type = event.sub_type
        flag = event.flag

        gconfig = GroupVerifyConfig()
        gconfig.getGroupConfig(gid)

        if gconfig.isEnable:
            password = gconfig.Password if gconfig.isAuto else None

            # 使用预编译正则进行匹配
            match = ANSWER_PATTERN.search(comment)
            result = match.group(1).strip() if match else comment.strip()

            # 使用元组保持不可变性，顺序敏感的匹配模式
            MARK_PATTERNS = (("来交流学习的", "Advertise"),)

            if password is not None and result == password:
                await bot.set_group_add_request(
                    flag=flag, sub_type=sub_type, approve=True
                )
                await matcher.send(
                    f"已自动同意 QQ 号 {uid} 入群！\n他的入群答案是：{result}"
                )
            else:
                # 单次遍历匹配所有模式
                matched = next(
                    (mark for keyword, mark in MARK_PATTERNS if keyword in result), None
                )
                if matched:
                    await bot.set_group_add_request(
                        flag=flag,
                        sub_type=sub_type,
                        approve=False,
                        reason="bot自动处理：建议更换入群答案重新申请",
                    )
                    await matcher.send(
                        f"已自动拒绝 QQ 号 {uid} 入群！\n他的入群答案是：{result}\n\n标记：{matched}"
                    )
                else:
                    await matcher.send(
                        f"QQ 号 {uid} 申请入群！\n他的入群答案是：\n{comment}\n\n事件编号：{flag}"
                    )
    except Exception as e:
        # 建议在此处补充日志记录
        await matcher.send(f"事件处理失败: {e}")


def get_man_argument_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("-s", "--status", type=int, default=0)
    parser.add_argument("-a", "--auto", type=int, default=0)
    parser.add_argument("-p", "--password", type=str, default="")
    return parser


class ManagerArguments(BaseModel):
    status: int
    auto: int
    password: str


def man_parse_from_parser(args: Namespace) -> ManagerArguments:
    """解析查询命令参数"""
    return ManagerArguments.model_validate(vars(args))


def get_shell_command_parse_failed_handler() -> T_Handler:
    """构造处理解析 Shell 命令失败的 handler"""

    async def handle_parse_failed(
        matcher: Matcher, shell_args: Annotated[ParserExit, ShellCommandArgs()]
    ):
        """解析命令失败"""
        await matcher.finish("命令格式错误, 请确认后再重试吧\n" + shell_args.message)

    return handle_parse_failed


@on_startswith(
    msg=("同意", "拒绝"),
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=20,
    block=True,
).handle()
async def handle_parse_group_request(
    bot: Bot, event: GroupMessageEvent, matcher: Matcher
) -> None:
    try:
        if not event.reply:
            return

        reply_msg = str(event.reply.message).split()
        if not reply_msg:
            await matcher.send("无效的回复消息格式", reply_message=True)
            return

        # 处理事件编号
        event_id_part = reply_msg[-1]
        if not event_id_part.startswith("事件编号："):
            await matcher.send("未找到有效的事件编号", reply_message=True)
            return

        flag = str(event_id_part.replace("事件编号：", "", 1)).strip()
        if not flag:
            await matcher.send("事件编号不能为空", reply_message=True)
            return

        # 处理审批操作
        original_msg = str(event.message)
        approve = original_msg.startswith("同意")
        reason = (
            original_msg.replace("拒绝", "", 1)
            .replace(",", " ")
            .replace("，", " ")
            .strip()
            if not approve
            else ""
        )

        # 执行审批操作
        await bot.set_group_add_request(flag=flag, approve=approve, reason=reason)
        await matcher.send(
            f"已{'同意' if approve else '拒绝'}入群请求", reply_message=True
        )

    except Exception as e:
        await matcher.send(f"处理请求时发生意外错误: {str(e)}", reply_message=True)


@on_shell_command(
    "gspm",
    aliases={"加群管理"},
    parser=get_man_argument_parser(),
    handlers=[get_shell_command_parse_failed_handler()],
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=20,
    block=True,
).handle()
async def handle_parsed_success(
    event: GroupMessageEvent,
    matcher: Matcher,
    args: Annotated[Namespace, ShellCommandArgs()],
):
    try:
        gid = str(event.group_id)
        args = man_parse_from_parser(args=args)
        enabled = bool(args.status)
        auto = bool(args.auto)
        password = args.password

        gconfig = GroupVerifyConfig()
        gconfig.updateConfig(gid, isEnable=enabled, isAuto=auto, Password=password)

        await matcher.finish("已更新配置")
    except Exception as e:
        await matcher.send(f"配置更新失败: {e}")
