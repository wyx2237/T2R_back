"""计算会话管理 —— 内存字典存储，管理上传 → 选指标 → 执行 三阶段"""

import asyncio
from datetime import datetime, timezone, timedelta
import json
from uuid import uuid4

from models.compute import ComputeSession, MetricComputeResult
from models.metric import Metric
from services.core import recommand
from services import metric_store


_sessions: dict[str, ComputeSession] = {}

# 后台清理配置
_CLEANUP_INTERVAL_SECONDS = 600  # 每 10 分钟清理一次
_SESSION_TTL = timedelta(minutes=30)  # 会话最多保留 30 分钟

_cleanup_task: asyncio.Task | None = None


async def _cleanup_loop():
    """后台定时清理过期会话，防止内存泄漏。"""
    while True:
        await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)
        now = datetime.now(timezone.utc)
        expired = [
            sid
            for sid, s in list(_sessions.items())
            if now - datetime.fromisoformat(s.createdAt) > _SESSION_TTL
        ]
        for sid in expired:
            del _sessions[sid]
        if expired:
            print(f"[Session Cleanup] 已清理 {len(expired)} 个过期会话")


def _start_cleanup():
    """惰性启动后台清理任务（确保在事件循环运行时调用）。"""
    global _cleanup_task
    if _cleanup_task is not None:
        return
    try:
        _cleanup_task = asyncio.create_task(_cleanup_loop())
    except RuntimeError:
        pass  # 事件循环尚未运行，等下次 create_session 时再试


async def create_session(raw_text: str, all_metrics: list[Metric]) -> ComputeSession:
    """上传文件后创建新会话，返回带 sessionId 的会话对象"""
    _start_cleanup()  # 惰性启动后台清理任务
    # 只保留 metric 元信息字段
    available_metrics = [
        {   
            "id": metric.id,
            "name": metric.name,
            "description": metric.description,
            "department": metric.department,
            "inputs": metric.inputs,
        }
        for metric in all_metrics
    ]
    recommand_metrics = await recommand.recommand(raw_text, available_metrics, 5)  # 先占位
    print(f"[Recommand Metrics]: \n{json.dumps(recommand_metrics, ensure_ascii=False, indent=4)}")
    standard_metrics = [
        m.model_dump()
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
