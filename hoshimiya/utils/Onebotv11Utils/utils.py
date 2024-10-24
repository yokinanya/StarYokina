import json
import math
import os
import pathlib
import sys
from typing import Union

import httpx
from nonebot import logger


LOCAL_TMP_DIR = (
    pathlib.Path(os.path.abspath(sys.path[0])).joinpath("hoshimiya").joinpath(".tmp")
)
OMEGA_LOCAL_TMP_DIR = pathlib.Path(os.path.abspath(sys.path[0])).joinpath(".tmp")
if not os.path.exists(LOCAL_TMP_DIR):
    os.makedirs(LOCAL_TMP_DIR)


async def download_url(url: str, max_retry: int = 3) -> bytes:
    """
    下载传入url，支持失败重试
    :param url: str
    :return: bytes
    """
    async with httpx.AsyncClient() as client:
        for i in range(max_retry):
            try:
                resp = await client.get(url)
                if resp.status_code != 200:
                    continue
                return resp.content
            except Exception as e:
                logger.error(f"Error downloading {url}, retry {i}/max_retry: {str(e)}")


async def save_download(url: str, module: str, save_file_name: str) -> pathlib.Path:
    if not os.path.exists(LOCAL_TMP_DIR.joinpath(module)):
        os.makedirs(LOCAL_TMP_DIR.joinpath(module))
    save_dir = LOCAL_TMP_DIR.joinpath(module).joinpath(save_file_name)
    with open(save_dir, "wb") as file:
        content = await download_url(url)
        file.write(content)
    logger.debug(f"Save Download | save {url} to {save_dir}")
    return save_dir


async def download_avatar(uid: str) -> bytes:
    """
    根据 qq号 获取头像
    :param uid: str
    :return: bytes
    """
    url = f"http://q1.qlogo.cn/g?b=qq&nk={uid}&s=640"
    data = await download_url(url)
    if not data:
        url = f"http://q1.qlogo.cn/g?b=qq&nk={uid}&s=100"
        data = await download_url(url)
    return data


def AtSB(data: str) -> Union[list[str], list[int], list]:
    """
    检测at了谁，返回[qq, qq, qq,...]
    包含全体成员直接返回['all']
    如果没有at任何人，返回[]
    :param data: event.json
    :return: list
    """
    try:
        qq_list = []
        data = json.loads(data)
        for msg in data["message"]:
            if msg["type"] == "at":
                if "all" not in str(msg):
                    qq_list.append(int(msg["data"]["qq"]))
                else:
                    return ["all"]
        return qq_list
    except KeyError:
        return []


def convert_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0B"
    size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i-1]}"
