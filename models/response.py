"""统一响应模型"""

from typing import Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    message: str # 消息提示
    data: Any = None # 返回数据
    status_code: int = 200 # 状态码
