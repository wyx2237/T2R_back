"""指标管理路由 —— 对应 API.md §2.1 ~ §2.5"""

from fastapi import APIRouter, Query

from models.metric import CreateMetricRequest
from models.response import ResponseModel
from services import metric_store

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
def list_metrics(
    keyword: str | None = Query(None),
    department: str | None = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=1000),
) -> ResponseModel:
    """分页查询指标列表，支持关键词搜索和科室筛选，对应 API.md §2.1"""
    data = metric_store.list_metrics(
        keyword=keyword,
        department=department,
        page=page,
        page_size=pageSize,
    )
    return ResponseModel(message="查询成功", data=data)


@router.get("/metrics/{metric_id}")
def get_metric(metric_id: str) -> ResponseModel:
    """获取单个指标详情，对应 API.md §2.2"""
    metric = metric_store.get_metric_by_id(metric_id)
    if metric is None:
        return ResponseModel(message="指标不存在", status_code=404)
    return ResponseModel(message="查询成功", data=metric)


@router.post("/metrics", status_code=200)
def create_metric(body: CreateMetricRequest) -> ResponseModel:
    """
    创建医学临床计算指标

    body:
        question(str): 指标计算的目标问题
        formula(str): 对指标的计算方式的完整定义
    """
    metric = metric_store.create_metric(body.question, body.formula)
    return ResponseModel(message="创建成功", data={"metricId": metric.id})


@router.put("/metrics/{metric_id}", status_code=200)
def update_metric(metric_id: str, body: dict) -> ResponseModel:
    """
    编辑、更新指标
    """
    metric = metric_store.update_metric(metric_id, body)
    if metric is None:
        return ResponseModel(message="指标不存在", status_code=404)
    return ResponseModel(message="更新成功", data={"metricId": metric.id})


@router.delete("/metrics/{metric_id}", status_code=200)
def delete_metric(metric_id: str) -> ResponseModel:
    """删除指标，对应 API.md §2.5"""
    ok = metric_store.delete_metric(metric_id)
    if not ok:
        return ResponseModel(message="指标不存在", status_code=404)
    return ResponseModel(message="删除成功", data={"metricId": metric_id})
