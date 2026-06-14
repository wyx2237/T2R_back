"""工具模板路由 —— GET /api/tools"""

from fastapi import APIRouter

from models.response import ResponseModel
from services import tool_store

router = APIRouter(tags=["Tools"])


@router.get("/tools")
def get_tools() -> ResponseModel:
    """获取全部 8 个原子工具模板，对应 API.md §1.1"""
    tools = tool_store.get_all_tools()
    return ResponseModel(message="查询成功", data=tools)
