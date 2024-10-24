import asyncio
import os
import pathlib
import subprocess
from datetime import datetime
from typing import Union


from hoshimiya.utils.CoreManager import PluginLock
from hoshimiya.utils.Onebotv11Utils import save_download
from hoshimiya.utils.Onebotv11Utils.utils import LOCAL_TMP_DIR
from nonebot import logger

ReverseGifLock = PluginLock(name="reversegif")


async def ReverseGif(url: str) -> Union[pathlib.Path | None]:
    now_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    source = await save_download(url, "gif", f"reverse_gif_{now_time}.gif")
    output = LOCAL_TMP_DIR.joinpath("gif").joinpath(
        f"reverse_gif_{now_time}_output.gif"
    )

    # 清理旧缓存
    tmp_files = os.listdir(LOCAL_TMP_DIR.joinpath("gif"))
    tmp_files.remove(f"reverse_gif_{now_time}.gif")
    for tmp_file in tmp_files:
        tmp_file = LOCAL_TMP_DIR.joinpath("gif").joinpath(tmp_file)
        os.remove(tmp_file)

    if os.path.getsize(source) > 3 * 1024 * 1024:
        return None
    # 加锁
    ReverseGifLock.locker("lock")

    try:
        # ffmpeg
        # options = ["-vf", "reverse"]
        # subprocess.call(["ffmpeg", "-i", source, *options, "-y", output])

        # ImageMagick
        options = ["-coalesce", "-reverse"]
        subprocess.call(["convert", source, *options, output])

        # 等待图像输出
        return output
    except Exception as e:
        logger.error(e)
    finally:
        ReverseGifLock.locker("unlock")
