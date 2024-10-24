import re
from typing import Annotated

from nonebot import on_request, on_shell_command, on_startswith
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, GroupRequestEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.rule import ArgumentParser, Namespace
from nonebot.typing import T_Handler
from pydantic import BaseModel

from .model import GroupVerifyConfig

new_member = on_request()


@new_member.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    comment = event.comment
    gid = event.group_id
    uid = event.user_id
    sub_type = event.sub_type
    flag = event.flag
    gconfig = GroupVerifyConfig()
    gconfig.getGroupConfig(gid)
    if gconfig.isEnable is True:
        if gconfig.isAuto is True:
            password = gconfig.Password
            match = re.search(r"答案：(.*)", comment)
            if match:
                result = match.group(1).strip()
            else:
                result = comment.strip()
            if result == password:
                await bot.set_group_add_request(
                    flag=flag, sub_type=sub_type, approve=True
                )
                await bot.send(
                    event, f"已自动同意 QQ 号 {uid} 入群！\n他的入群答案是：{result}"
                )
            else:
                await bot.send(
                    event,
                    f"QQ 号 {uid} 申请入群！\n他的入群答案是：\n{comment}\n\n事件编号：{flag}",
                )
        else:
            await bot.send(
                event,
                f"QQ 号 {uid} 申请入群！\n他的入群答案是：\n{comment}\n\n事件编号：{flag}",
            )


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
async def handle_parse_group_request(bot: Bot, event: GroupMessageEvent) -> None:
    if event.reply:
        original_reply_message = str(event.reply.message).split()
        original_message = str(event.message)

        if original_reply_message[-1].startswith("事件编号："):
            flag = original_reply_message[-1].replace("事件编号：", "", 1)

        if original_message.startswith("同意"):
            reason = ""
            approve = True
        elif original_message.startswith("拒绝"):
            reason = (
                original_message.replace(",", " ")
                .replace("，", " ")
                .replace("拒绝", "")
            )
            approve = False

        try:
            await bot.set_group_add_request(
                flag=flag,
                approve=approve,
                reason=reason,
            )
            if approve is True:
                await bot.send(event, f"已同意入群请求", reply_message=True)
            else:
                await bot.send(event, f"已拒绝入群请求", reply_message=True)
        except Exception as e:
            await bot.send(event, f"事件处理失败: {e}", reply_message=True)


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
    gid = str(event.group_id)
    args = man_parse_from_parser(args=args)
    enabled = bool(args.status)
    auto = bool(args.auto)
    password = args.password
    GroupVerifyConfig().getGroupConfig(gid)
    GroupVerifyConfig(isEnable=enabled, isAuto=auto, Password=password).updateConfig(
        gid
    )
    await matcher.finish("已更新配置")
