"""计算会话管理 —— 内存字典存储，管理上传 → 选指标 → 执行 三阶段"""

import asyncio
from datetime import datetime, timezone, timedelta
import json
import random
from pathlib import Path
from uuid import uuid4

from models.compute import ComputeSession, MetricComputeResult
from models.metric import Metric
from services.core import recommand
from services import metric_store

# patient_metrics_mapping.json 的路径
_MAPPING_FILE = Path(__file__).resolve().parent.parent / "data" / "patient_metrics_mapping.json"


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


async def create_session(
    raw_text: str,
    all_metrics: list[Metric],
    predefined_metric_codes: list[str] | None = None,
) -> ComputeSession:
    """上传文件后创建新会话，返回带 sessionId 的会话对象"""
    _start_cleanup()  # 惰性启动后台清理任务
    # 只保留 metric 元信息字段
    available_metrics = [
        {
            "id": metric.id,
            "code": metric.code,
            "name": metric.name,
            "description": metric.description,
            "department": metric.department,
            "inputs": metric.inputs,
        }
        for metric in all_metrics
    ]

    if predefined_metric_codes:
        # 使用 patient_metrics_mapping.json 中预定义的指标，不走大模型推荐
        recommand_metrics = _build_mapped_recommand(
            predefined_metric_codes, available_metrics
        )
    else:
        recommand_metrics = await recommand.recommand(raw_text, available_metrics, 5)

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


def _build_mapped_recommand(
    metric_codes: list[str],
    available_metrics: list[dict],
) -> list[dict]:
    """根据预定义的指标 code 列表，从 available_metrics 中匹配并构造 recommand 格式的结果。

    从匹配到的指标中随机选取 3~5 个，生成与 LLM 推荐相同格式的输出。
    """
    # 建立 code -> metric info 的映射
    code_to_metric: dict[str, dict] = {}
    for m in available_metrics:
        code_to_metric[m["code"]] = m

    # 匹配预定义 code 到 available_metrics
    matched: list[dict] = []
    for code in metric_codes:
        if code in code_to_metric:
            matched.append(code_to_metric[code])

    if not matched:
        return []

    # 随机选取 3~5 个
    k = random.randint(3, min(5, len(matched)))
    selected = random.sample(matched, k)

    # 构造与 LLM recommand 相同格式的输出
    result = []
    for m in selected:
        result.append({
            "indicatorId": m["id"],
            "indicatorName": m["name"],
            "scoreA": 3,
            "scoreB": 3,
            "scoreLabel": "a[3]+b[3]",
            "recommend": True,
            "reasonA": "基于预定义病例-指标映射推荐",
            "reasonB": "预定义映射中已包含该指标",
            "overallReason": f"该病例文件匹配预定义映射，推荐计算{m['name']}",
        })
    return result


def load_patient_metrics_mapping() -> dict[str, list[dict]]:
    """加载 patient_metrics_mapping.json，返回 {filename: [指标列表]} 的字典。"""
    if not _MAPPING_FILE.exists():
        return {}
    with open(_MAPPING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


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
