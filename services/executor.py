"""计算执行引擎 —— 根据指标定义构造逐步骤计算结果"""

import re
from typing import Any, Dict, List

from models.metric import Metric, WorkflowStep
from models.compute import MetricComputeResult, ExtractedParam, StepTrace, StepTraceInput, StepTraceOutput
from services.core import srge

async def execute(metric: Metric, raw_text: str) -> MetricComputeResult:
    """
    根据指标定义和原始文本执行计算，返回完整的 MetricComputeResult。

    原型阶段：模拟执行，返回结构正确的结果。
    后续可替换为真正的 executableCode 执行引擎。
    """
    workflow = metric.model_dump()
    extract_param_list = await srge.extract_parameters(workflow=workflow, patient_info=raw_text)  # 提取参数
    # 检查参数抽取结果
    check_result = check_extract_params(extract_param_list)
    # 格式转换
    extracted_params = build_extract_params(extract_param_list, raw_text)
    input_params = build_input_params(extract_param_list)
    input_units = build_input_units(extract_param_list)

    if check_result["valid"]:
        # 抽取正常：执行计算步骤追踪
        cal_result = srge.execute_code(code=workflow.get("executableCode"), input_params=input_params)
        print(f"【计算结果 cal_result】：\n{cal_result}")
        step_traces = build_step_traces(cal_result=cal_result, workflow_steps=metric.steps, input_params=input_params, input_units=input_units)
        return MetricComputeResult(
            metricId=metric.id,
            metricName=metric.name,
            metricCode=metric.code,
            finalValue=cal_result.get("final_value", 0.0),
            finalUnit=metric.output.output_unit,
            status="success",
            statusLabel="success",
            referenceRange={"min": 0, "max": 0},
            steps=step_traces,
            extractedParams=extracted_params,
        )
    else:
        # 抽取异常：返回错误信息，不执行后续计算
        error_messages = [e["message"] for e in check_result["errors"]]
        error_detail = "; ".join(error_messages)
        return MetricComputeResult(
            metricId=metric.id,
            metricName=metric.name,
            metricCode=metric.code,
            finalValue=0.0,
            finalUnit=metric.output.output_type,
            status="error",
            statusLabel=f"failed",
            referenceRange=None,
            steps=[],
            extractedParams=extracted_params,
        )
    
def check_extract_params(extract_param_list: List[Dict]) -> Dict[str, Any]:
    """
    检查参数抽取结果是否全部正常。
    如果出现参数 rawValue 为空或者 normalizedValue 为空（空字符串或 None），则返回具体错误信息。

    Args:
        input_params: ExtractedParam 结构的字典列表

    Returns:
        { "valid": bool, "errors": [ { "name": str, "field": str, "message": str }, ... ] }
    """
    errors: List[Dict[str, str]] = []

    for param in extract_param_list:
        name = param.get("name", "unknown")
        raw_value = param.get("rawValue")
        normalized_value = param.get("normalizedValue")

        # 检查 rawValue：不能为空字符串或 None
        if raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == ""):
            errors.append({
                "name": name,
                "field": "rawValue",
                "message": f"参数 '{name}' 的 rawValue 为空，原文中未找到对应值",
            })

        # 检查 normalizedValue：不能为 None
        if normalized_value is None:
            errors.append({
                "name": name,
                "field": "normalizedValue",
                "message": f"参数 '{name}' 的 normalizedValue 为空，无法标准化",
            })

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }
    
def build_input_params(extract_param_list: List[Dict]) -> Dict[str, Any]:
    """
    将 ExtractedParam 列表形式转换为 execute_code 所需的扁平键值对 dict 形式。

    key 为参数名 name
    value 为参数值 normalizedValue

    Args:
        extract_param_list: ExtractedParam 结构的字典列表

    Returns:
        { "age": 45, "gender": "male", ... }
    """
    return {
        param["name"]: param["normalizedValue"]
        for param in extract_param_list
    }

def build_input_units(extract_param_list: List[Dict]) -> Dict[str, str]:
    """
    从 ExtractedParam 列表提取参数单位映射 { param_name: unit }。

    Args:
        extract_param_list: ExtractedParam 结构的字典列表

    Returns:
        { "SerumCreatinine": "mg/dL", "Age": "years", ... }
    """
    return {
        param["name"]: param.get("unit", "")
        for param in extract_param_list
    }


def build_extract_params(extract_param_list: List[Dict], raw_text: str = "") -> List[ExtractedParam]:
    """
    将输入参数字典列表转换为 ExtractedParam 对象列表。

    Args:
        input_params: ExtractedParam 结构的字典列表
        raw_text: 原始文本（预留，用于位置校验）

    Returns:
        List[ExtractedParam]
    """
    extracted_params: List[ExtractedParam] = []
    for param in extract_param_list:
        position = _get_param_position(param.get("rawValue", ""), raw_text)
        extracted_params.append(ExtractedParam(
            name=param.get("name", ""),
            rawValue=param.get("rawValue", ""),
            normalizedValue=param.get("normalizedValue") if param.get("normalizedValue") is not None else "",
            unit=param.get("unit", ""),
            confidence=param.get("confidence", 0),
            position=position,
        ))
    return extracted_params

def _get_param_position(raw_value: str, raw_text: str) -> Dict[str, int]:
    """获取 rawValue 在 raw_text 中首次出现的位置。"""
    if not raw_text or not raw_value:
        return {"start": -1, "end": -1}
    start = raw_text.find(raw_value)
    if start == -1:
        return {"start": -1, "end": -1}
    return {"start": start, "end": start + len(raw_value)}


def build_step_traces(cal_result: Dict[str, Any], workflow_steps: List[WorkflowStep], input_params: Dict, input_units: Dict[str, str] = None) -> List[StepTrace]:
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
    context = {
        "inputs": input_params,
        "steps": {}
    } # 上下文变量字典，保存原始和步骤的输出
    for order, (res_step, ws) in enumerate(zip(result_steps, workflow_steps), start=1):
        print(f"[cur order]: {order}")

        # 构建 inputs 列表
        input_list = []
        for inp in ws.step_inputs:
            print(f"[cur context]: {context}")
            if "$|inputs|" in inp.input_source:
                match = re.search(r"\$\|inputs\|\.(\w+)", inp.input_source)
                source_name = match.group(1)
                input_value = context["inputs"].get(source_name)
                input_unit = (input_units or {}).get(source_name, "")
            else:
                # 从 "$|N|.output_name" 中解析步骤序号
                print(f"[input source]: {inp.input_source}")
                match = re.search(r"\$\|(\d+)\|\.(\w+)", inp.input_source)
                source_order = match.group(1)
                source_name = match.group(2)
                input_value = context["steps"][source_order].get(source_name, {}).get("value")
                input_unit = context["steps"][source_order].get(source_name, {}).get("unit")

            input_list.append(StepTraceInput(
                input_name=inp.input_name,
                input_value=input_value,
                input_unit=input_unit,
                input_source=inp.input_source,
            ))

        # 构建 outputs 列表
        step_result = res_step.get("step_result")
        unit = res_step.get("unit")
        output_list = []
        if isinstance(step_result, dict):
            for so in ws.step_outputs:
                output_list.append(StepTraceOutput(
                    output_name=so.output_name,
                    output_value=step_result.get(so.output_name),
                    output_unit=unit,
                ))
            context["steps"][str(order)] = {"value": step_result, "unit": unit}
        else:
            if ws.step_outputs:
                output_list.append(StepTraceOutput(
                    output_name=ws.step_outputs[0].output_name,
                    output_value=step_result,
                    output_unit=unit,
                ))
                context["steps"][str(order)] = {ws.step_outputs[0].output_name: {"value": step_result, "unit":unit}}
            else:
                context["steps"][str(order)] = {}

        trace = StepTrace(
            order=order,
            category=ws.category,
            step_name=ws.step_name,
            step_description=ws.step_description,
            step_detail=ws.detail,
            inputs=input_list,
            outputs=output_list,
            status="success",       # 默认成功
            errorMessage=None
        )
        traces.append(trace)
    return traces