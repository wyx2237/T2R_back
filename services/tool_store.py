"""工具模板服务 —— 从 tools.json 只读加载 8 个原子工具模板"""

import json
import os

from models.tool import AtomicTool


_tools: list[AtomicTool] = []


def load_tools(json_path: str = "data/tools.json") -> None:
    """启动时从 JSON 文件加载工具模板到内存"""
    if not os.path.exists(json_path):
        return
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _tools.clear()
    _tools.extend(AtomicTool(**item) for item in data)


def get_all_tools() -> list[AtomicTool]:
    """返回全部工具模板列表"""
    return _tools
