# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/16 10:15
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : utils.py
# @Software: PyCharm
import json
import random
from typing import Optional

import nonebot
from nonebot import get_driver, logger
from nonebot.adapters.onebot.v11 import ActionFailed, Bot
from nonebot.matcher import Matcher

from .config import qqmanager_plugin_config

su = get_driver().config.superusers
cb_notice = qqmanager_plugin_config.callback_notice

def MsgText(data: str):
    """
    返回消息文本段内容(即去除 cq 码后的内容)
    :param data: event.json()
    :return: str
    """
    try:
        data = json.loads(data)
        # 过滤出类型为 text 的【并且过滤内容为空的】
        msg_text_list = filter(lambda x: x['type'] == 'text' and x['data']['text'].replace(' ', '') != '', data['message'])
        # 拼接成字符串并且去除两端空格
        msg_text = ' '.join(map(lambda x: x['data']['text'].strip(), msg_text_list)).strip()
        return msg_text
    except:
        return ''



async def banSb(gid: int, ban_list: list, time: int = -1):
    """
    构造禁言
    :param gid: 群号
    :param time: 时间 (sec)
    :param ban_list: at列表
    :return:禁言操作
    """
    if 'all' in ban_list:
        yield nonebot.get_bot().set_group_whole_ban(
            group_id=gid,
            enable=True
        )
    else:
        if time is -1:
            time = random.randint(qqmanager_plugin_config.ban_rand_time_min, qqmanager_plugin_config.ban_rand_time_max)
        for qq in ban_list:
            if int(qq) in su or str(qq) in su:
                logger.info(f"SUPERUSER无法被禁言, {qq}")
                if cb_notice:
                    await nonebot.get_bot().send_group_msg(group_id = gid, message = 'SUPERUSER无法被禁言')
            else:
                yield nonebot.get_bot().set_group_ban(
                    group_id=gid,
                    user_id=qq,
                    duration=time,
                )


async def change_s_title(bot: Bot, matcher: Matcher, gid: int, uid: int, s_title: Optional[str]):
    """
    改头衔
    :param bot: bot
    :param matcher: matcher
    :param gid: 群号
    :param uid: 用户号
    :param s_title: 头衔
    """
    try:
        await bot.set_group_special_title(
            group_id=gid,
            user_id=uid,
            special_title=s_title,
            duration=-1,
        )
        await log_fi(matcher, f"头衔操作成功:{s_title}")
    except ActionFailed:
        logger.info('权限不足')


async def sd(cmd: Matcher, msg, at=False) -> None:
    if cb_notice:
        await cmd.send(msg, at_sender=at)


async def log_sd(cmd: Matcher, msg, log: str = None, at=False, err=False) -> None:
    (logger.error if err else logger.info)(log if log else msg)
    await sd(cmd, msg, at)


async def fi(cmd: Matcher, msg) -> None:
    await cmd.finish(msg if cb_notice else None)


async def log_fi(cmd: Matcher, msg, log: str = None, err=False) -> None:
    (logger.error if err else logger.info)(log if log else msg)
    await fi(cmd, msg)


def err_info(e: ActionFailed) -> str:
    e1 = 'Failed: '
    if e2 := e.info.get('wording'):
        return e1 + e2
    elif e2 := e.info.get('msg'):
        return e1 + e2
    else:
        return repr(e)