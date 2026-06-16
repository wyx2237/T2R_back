"""计算会话管理 —— 内存字典存储，管理上传 → 选指标 → 执行 三阶段"""

from datetime import datetime, timezone
from uuid import uuid4

from models.compute import ComputeSession, MetricComputeResult
from models.metric import Metric
from services.core import recommand
from services import metric_store


_sessions: dict[str, ComputeSession] = {}


async def create_session(raw_text: str, all_metrics: list[Metric]) -> ComputeSession:
    """上传文件后创建新会话，返回带 sessionId 的会话对象"""
    # 只保留 metric 元信息字段
    available_metrics = [
        {
            "name": metric.name,
            "description": metric.description,
            "department": metric.department,
            "inputs": metric.inputs,
        }
        for metric in all_metrics
    ]
    recommand_metrics = await recommand.recommand(raw_text, available_metrics, 5)  # 先占位
    standard_metrics = [
        m
        for metric in recommand_metrics
        if (m := metric_store.get_metric_by_id(metric.get("indicatorId"))) is not None
    ]
    session = ComputeSession(
        sessionId=uuid4().hex,
        rawText=raw_text,
        currentStep="upload",
        createdAt=datetime.now(timezone.utc).isoformat(),
    )
    _sessions[session.sessionId] = session
    return {
        "session": session.model_dump(),
        "recommand_metrics": recommand_metrics,
        "standard_metrics": standard_metrics
    }


def get_session(session_id: str) -> ComputeSession | None:
    """根据 sessionId 获取会话，不存在返回 None"""
    return _sessions.get(session_id)


def set_selected_metric(session_id: str, metric_id: str) -> bool:
    """记录用户选中的指标 ID，同时推进 currentStep 到 'select'"""
    session = _sessions.get(session_id)
    if session is None:
        return False
    session.selectedMetricId = metric_id
    session.currentStep = "select"
    return True


def save_results(session_id: str, results: list[MetricComputeResult]) -> bool:
    """保存计算结果，推进 currentStep 到 'result'"""
    session = _sessions.get(session_id)
    if session is None:
        return False
    session.results = results
    session.currentStep = "result"
    return True


def has_results(session_id: str) -> bool:
    """判断会话是否已有可导出的计算结果"""
    session = _sessions.get(session_id)
    if session is None:
        return False
    return len(session.results) > 0
