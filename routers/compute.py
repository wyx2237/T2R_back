"""计算执行路由 —— 对应 API.md §3.1 ~ §3.4"""

from fastapi import APIRouter, UploadFile, File

from models.compute import ComputeSession, ExecuteRequest, MetricComputeResult
from models.response import ResponseModel
from services import session_manager, metric_store, executor
import json

router = APIRouter(prefix="/compute", tags=["Compute"])


@router.post("/sessions")
async def upload_case_file(file: UploadFile = File(...)) -> ResponseModel:
    """
    上传 .txt 病例文件，创建计算会话，返回可计算指标列表。
    对应 API.md §3.1
    
    Returns
        result:
            session: ComputeSession
            recommand_metrics: list
            standard_metrics: list
    """
    raw_text = (await file.read()).decode("utf-8")
    metrics = metric_store.list_metrics(page_size=1000).items
    result = await session_manager.create_session(raw_text, metrics)
    print(json.dumps(result, ensure_ascii=False, indent=4))
    return ResponseModel(message="创建成功", data=result)


@router.get("/sessions/{session_id}")
def get_session(session_id: str) -> ResponseModel:
    """获取会话当前状态，对应 API.md §3.2"""
    session = session_manager.get_session(session_id)
    if session is None:
        return ResponseModel(message="会话不存在", status_code=404)
    return ResponseModel(message="查询成功", data=session)


@router.post("/sessions/{session_id}/execute")
async def execute_compute(session_id: str, data: ExecuteRequest) -> ResponseModel:
    """
    提交选中的指标 ID 和原始文本，执行定量计算并返回逐步骤结果。
    对应 API.md §3.3
    """
    session = session_manager.get_session(session_id)
    if session is None:
        return ResponseModel(message="会话不存在", status_code=404)
    metric = metric_store.get_metric_by_id(data.metricId)
    if metric is None:
        return ResponseModel(message="指标不存在", status_code=404)
    session_manager.set_selected_metric(session_id, data.metricId)
    result = await executor.execute(metric, data.rawText)
    session_manager.save_results(session_id, [result])
    return ResponseModel(message="计算完成", data=result)


@router.get("/sessions/{session_id}/export")
def export_report(session_id: str) -> ResponseModel:
    """导出计算结果为markdown"""
    session = session_manager.get_session(session_id)
    if session is None:
        return ResponseModel(message="会话不存在", status_code=404)
    if not session_manager.has_results(session_id):
        return ResponseModel(message="尚无计算结果", status_code=400)
    md = _build_export_markdown(session)
    return ResponseModel(message="导出成功", data={"markdown": md})


def _build_export_markdown(session: ComputeSession) -> str:
    """根据会话结果拼接导出 Markdown"""
    lines: list[str] = []
    lines.append("# 计算报告")
    lines.append("")
    lines.append(f"- 会话ID: {session.sessionId}")
    lines.append(f"- 原始文本: {session.rawText}")
    lines.append("")
    for i, r in enumerate(session.results, 1):
        lines.append(f"## 结果 {i}: {r.metricName}({r.metricCode})")
        lines.append("")
        lines.append(f"- 最终值: {r.finalValue} {r.finalUnit}")
        lines.append(f"- 状态: {r.statusLabel}")
        lines.append(f"- 参考范围: {r.referenceRange}")
    return "\n".join(lines)
