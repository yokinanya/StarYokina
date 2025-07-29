import asyncio
import json
from typing import Dict

from nonebot.adapters.onebot.v11 import MessageSegment

from hoshimiya.utils.Onebotv11Utils.utils import LOCAL_DATA_DIR

# 内存中的群配置缓存，key 为群号，value 为 openai_enabled 状态
openai_enabled_ram: Dict[int, bool] = {}


class GroupConfig:
    """
    群配置类：用于存储和管理单个群的 OpenAI 功能开关。
    推荐通过 load_from_file 全局加载后再实例化对象。
    """

    def __init__(self, gid: int):
        self.gid: int = gid
        # 默认禁用 OpenAI 功能，优先从内存加载
        self.openai_enabled: bool = openai_enabled_ram.get(gid, False)

    def enable_openai(self) -> None:
        """启用 OpenAI 功能"""
        self.openai_enabled = True

    def disable_openai(self) -> None:
        """禁用 OpenAI 功能"""
        self.openai_enabled = False

    def load_from_ram(self) -> bool:
        """
        从内存缓存加载当前群的 openai_enabled 状态。
        返回值：当前群 openai_enabled 状态。
        """
        self.openai_enabled = openai_enabled_ram.get(self.gid, False)
        return self.openai_enabled

    def save(self) -> None:
        """
        保存当前群配置到内存缓存并写入文件。
        推荐统一调用本方法。
        """
        openai_enabled_ram[self.gid] = self.openai_enabled
        config_path = LOCAL_DATA_DIR.joinpath("llmchat_config.json")
        data: Dict[str, dict] = {}
        if config_path.exists():
            try:
                with config_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                data = {}
        data[str(self.gid)] = {"openai_enabled": self.openai_enabled}
        try:
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"[llmchat] 配置文件写入失败: {e}")

    @staticmethod
    def load_from_file() -> None:
        """
        从文件加载所有群配置到内存缓存。
        文件格式错误时清空缓存并打印警告。
        """
        config_path = LOCAL_DATA_DIR.joinpath("llmchat_config.json")
        if not config_path.exists():
            if openai_enabled_ram:
                openai_enabled_ram.clear()
            return
        try:
            with config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            openai_enabled_ram.clear()
            for gid, config in data.items():
                try:
                    openai_enabled_ram[int(gid)] = bool(
                        config.get("openai_enabled", False))
                except Exception:
                    continue
        except (json.JSONDecodeError, OSError):
            openai_enabled_ram.clear()
            print("[llmchat] 配置文件格式错误，已清空内存配置")


# 全局AI会话并发锁
_ai_chat_semaphore = asyncio.Semaphore(3)


async def ai_chat_acquire():
    """获取AI会话并发锁，超出3个直接raise"""
    if _ai_chat_semaphore.locked() and _ai_chat_semaphore._value == 0:
        raise RuntimeError("AI会话数已达上限，请稍后再试")
    await _ai_chat_semaphore.acquire()


def ai_chat_release():
    """释放AI会话并发锁"""
    _ai_chat_semaphore.release()


def generate_message_node(user_id: str, nickname: str, content: str) -> dict:
    """
    生成 NapCat 合并转发 node 节点，content 为消息段 dict 数组
    {"type": "node", "data": {"user_id": ..., "nickname": ..., "content": [...]}}
    """
    return {
        "type": "node",
        "data": {
            "user_id": int(user_id),
            "nickname": str(nickname),
            "content": content,
        }
    }


def generate_forward_message(group_id: str, messages: list) -> dict:
    """
    构造合并转发消息
    """
    forward_message = {
        "message_type": "group",
        "group_id": int(group_id),
        "messages": messages
    }
    print(f"[llmchat] 生成合并转发消息: {forward_message}")
    return forward_message


def segment_message(message: str) -> list[str]:
    """
    将LLM返回的消息分割成多个消息段 dict（NapCat node content 需要消息段数组）
    """
    lines = message.splitlines()
    segments = []
    buffer = ""
    for line in lines:
        if len(buffer) + len(line) + 1 <= 250:
            buffer += (line + "\n")
        else:
            if buffer:
                segments.append(
                    {"type": "text", "data": {"text": buffer.rstrip("\n")}})
            buffer = line + "\n"
    if buffer:
        segments.append(
            {"type": "text", "data": {"text": buffer.rstrip("\n")}})
    return segments
