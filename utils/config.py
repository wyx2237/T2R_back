import os
from dotenv import load_dotenv

# 加载 .env 文件（从当前文件所在项目的根目录）
load_dotenv()

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")