"""计算执行引擎 —— 根据指标定义构造逐步骤计算结果"""

from typing import Any, Dict, List
from models.metric import Metric, WorkflowStep
from models.compute import ComputeStepStatus, InputSourceItem, MetricComputeResult, ExtractedParam, StepTrace
from services.core import srge

def execute(metric: Metric, raw_text: str) -> MetricComputeResult:
    """
    根据指标定义和原始文本执行计算，返回完整的 MetricComputeResult。


    原型阶段：模拟执行，返回结构正确的结果。
    后续可替换为真正的 executableCode 执行引擎。
    """
    metric_dict = metric.model_dump()  # 将 Metric 对象转换为字典
    input_params, cal_result = srge.calculate(workflow=metric, patient_info=raw_text) # 先占位
    steps = metric_dict.get("steps", [])
    # 将step结果与定义信息合并，处理为stepTrace
    StepTraces = build_step_traces(cal_result=cal_result, workflow_steps=steps)

    return MetricComputeResult(
        metricId=metric.id,
        metricName=metric.name,
        metricCode=metric.code,
        finalValue=cal_result.get("final_value", None),
        finalUnit=metric.output.output_type,
        status="normal",
        statusLabel="正常",
        referenceRange={"min": 0, "max": 0},
        steps=StepTraces,
        extractedParams=None,
    )

def build_extract_params(input_params: Dict[str, Any]) -> List[ExtractedParam]:
    """
    将输入参数转换为 ExtractedParam 列表。
    """

    extracted_params = []
def build_step_traces(cal_result: Dict[str, Any], workflow_steps: List[WorkflowStep]) -> List[StepTrace]:
    """
    将计算结果和 workflow 步骤定义按顺序转换为 StepTrace 列表。

    Args:
        cal_result: 包含 "steps" 列表的字典，每个元素包含 step_name, step_result, unit。
        workflow_steps: 按执行顺序排列的 WorkflowStep 列表。

    Returns:
        List[StepTrace]: 按顺序排列的步骤追踪列表。
    """
    result_steps = cal_result.get("steps", [])
    # 按顺序一一对应，长度不一致时以短的为准
    traces = []
    for order, (res_step, ws) in enumerate(zip(result_steps, workflow_steps), start=1):
        # 构建 input 字典（输入值暂缺，设为 None）
        input_dict = {inp.input_name: None for inp in ws.step_inputs}
        # 构建 inputSource 字典
        input_source_dict = {
            inp.input_name: InputSourceItem(source=inp.input_source, description=inp.input_desc)
            for inp in ws.step_inputs
        }
        # 构建 output 字典（计算结果和单位）
        output_dict = {
            "result": res_step.get("step_result"),
            "unit": res_step.get("unit")
        }
        trace = StepTrace(
            order=order,
            toolId=f"tool_{ws.step_name}",          # 默认生成 toolId
            toolName=ws.step_name,
            description=ws.step_description,
            formulaLatex=None,                      # 缺失字段设 None
            input=input_dict,
            inputSource=input_source_dict,
            output=output_dict,
            status=ComputeStepStatus.SUCCESS,       # 默认成功
            errorMessage=None
        )
        traces.append(trace)
    return traces