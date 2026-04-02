# 导入 os 模块，用来读取环境变量
import os

# 从 python-dotenv 导入 load_dotenv
# 它的作用是把 .env 文件里的配置加载到当前程序环境里
from dotenv import load_dotenv


# 执行这行后，项目根目录里的 .env 文件就会被读取
load_dotenv()


# 读取 API Key
# 如果没读到，就返回空字符串 ""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 读取 API Base URL
# 这里默认值直接写成 MiniMax 的兼容地址
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.minimaxi.com/v1")

# 读取模型名
# 如果 .env 里没配，就默认使用 MiniMax-M2.5-highspeed
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "MiniMax-M2.5-highspeed")


# 做一个最基础的保护：
# 如果没有读取到 API Key，就直接报错，提醒你检查 .env
if not OPENAI_API_KEY:
    raise ValueError("未读取到 OPENAI_API_KEY，请检查 .env 文件配置。")