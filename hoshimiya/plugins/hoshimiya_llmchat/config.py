from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    # LLMChat API 配置
    llmchat_api_base_url: str = "https://api.openai.com/v1"
    llmchat_api_key: str = ""
    llmchat_model: str = "gpt-3.5-turbo"
    llmchat_temperature: float = 0.7
    llmchat_max_tokens: int = 1000
    # 每个用户每天可以调用的次数限制
    llmchat_daily_limit: int = 10


# 配置加载
plugin_config: Config = get_plugin_config(Config)
global_config = get_driver().config

# 全局名称
NICKNAME: str | None = next(iter(global_config.nickname), None)
