"""原子工具模板相关 Pydantic 模型，对应 API.md §1 + 附录"""

from pydantic import BaseModel


class MetaInfo(BaseModel):
    Name: str
    Description: str
    Scope: str


class FlowItem(BaseModel):
    Description: str
    Example: dict


class FlowInfo(BaseModel):
    Input: FlowItem
    Output: FlowItem


class ExecInfo(BaseModel):
    Language: str
    Library: list[str]
    Logic: list[str]


class ToolExample(BaseModel):
    ToolName: str
    Parameters: dict
    Code: str
    Output: dict


class AtomicTool(BaseModel):
    id: str
    MetaInfo: MetaInfo
    FlowInfo: FlowInfo
    ExecInfo: ExecInfo
    Examples: list[ToolExample]
