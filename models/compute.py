"""计算执行相关 Pydantic 模型，对应 API.md §3 + 附录"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from models.metric import Metric

# ── 枚举类型 ──

ComputeStepStatus = Literal["success", "error"]
ResultStatus = Literal["success", "error", "normal", "borderline", "abnormal"]
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

class StepTraceInput(BaseModel):
    input_name: str
    input_value: Any | None = None
    input_unit: str | None = None
    input_source: str  # "$|inputs|.xxx" 或 "$|steps|.N.output_name"


class StepTraceOutput(BaseModel):
    output_name: str
    output_value: Any | None = None
    output_unit: str | None = None


class StepTrace(BaseModel):
    order: int
    category: str
    step_name: str
    step_description: str
    inputs: list[StepTraceInput]
    outputs: list[StepTraceOutput]
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
