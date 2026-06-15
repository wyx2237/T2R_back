"""计算执行相关 Pydantic 模型，对应 API.md §3 + 附录"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from models.metric import Metric

# ── 枚举类型 ──

ComputeStepStatus = Literal["success", "error"]
ResultStatus = Literal["success", "error", "normal", "borderline", "abnormal"]
SourceType = Literal["raw", "step"]
SessionStep = Literal["upload", "select", "result"]


# ── 参数抽取 ──

class ExtractedParam(BaseModel):
    name: str
    rawValue: str
    normalizedValue: str | float
    unit: str
    confidence: int  # 0~5
    position: dict  # { start: int, end: int }


# ── 步骤追溯 ──

class InputSourceItem(BaseModel):
    sourceType: SourceType
    sourceLabel: str


class StepTrace(BaseModel):
    order: int
    toolId: str
    toolName: str
    description: str
    formulaLatex: str | None = None
    input: dict
    inputSource: dict[str, InputSourceItem]
    output: dict
    status: ComputeStepStatus
    errorMessage: str | None = None


# ── 计算结果 ──

class MetricComputeResult(BaseModel):
    metricId: str
    metricName: str
    metricCode: str
    finalValue: float
    finalUnit: str
    status: ResultStatus | None = None
    statusLabel: str | None = None
    referenceRange: dict | None = None  # { min, max }
    steps: list[StepTrace]
    extractedParams: list[ExtractedParam]


# ── 计算会话 ──

class ComputeSession(BaseModel):
    sessionId: str
    rawText: str
    selectedMetricId: str | None = None
    results: list[MetricComputeResult] = []
    currentStep: SessionStep = "upload"
    createdAt: str  # ISO 8601


# ── 请求体 ──

class ExecuteRequest(BaseModel):
    metricId: str
    rawText: str


class MetricListResponse(BaseModel):
    items: list[Metric]
    total: int
