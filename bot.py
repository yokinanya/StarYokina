import os
import sys
import nonebot
from datetime import datetime
from nonebot.log import logger, default_format

# Log file path
bot_log_path = os.path.abspath(os.path.join(sys.path[0], 'log'))
if not os.path.exists(bot_log_path):
    os.makedirs(bot_log_path)

# Custom logger
log_info_name = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}-INFO.log'
log_error_name = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}-ERROR.log'
log_info_path = os.path.join(bot_log_path, log_info_name)
log_error_path = os.path.join(bot_log_path, log_error_name)

logger.add(log_info_path, rotation='00:00', diagnose=False, level='INFO', format=default_format, encoding='utf-8')
logger.add(log_error_path, rotation='00:00', diagnose=False, level='ERROR', format=default_format, encoding='utf-8')


# 初始化 NoneBot
nonebot.init()

# 获取 driver 用于初始化
driver = nonebot.get_driver()

# 按需注册 OneBot V11 Adapter
if driver.config.model_dump().get('onebot_access_token'):
    from nonebot.adapters.onebot.v11.adapter import Adapter as OneBotAdapter
    driver.register_adapter(OneBotAdapter)

# 在这里加载插件
# nonebot.load_builtin_plugins("echo")  # 内置插件
# nonebot.load_plugin("thirdparty_plugin")  # 第三方插件
nonebot.load_plugins("hoshimiya\plugins")  # 本地插件
nonebot.load_plugins("nbtest\plugins")
# nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run()