"""指标存储服务 —— 读写 metrics.json，支持分页查询和 CRUD"""
import sys
sys.path.append("/root/local/BIYELUNWEN/KAITI/DEMO/T2R_back")

import json
import os
import threading
import re

from models.metric import Metric
from models.compute import MetricListResponse

from services.core import srge, Tools

_metrics: list[Metric] = []
_lock = threading.Lock()
_json_path: str = "data/metrics.json"
_meta_path: str = "data/meta.json"


def load_metrics(json_path: str = "data/metrics.json") -> None:
    """启动时从 JSON 文件加载指标列表到内存"""
    global _metrics, _json_path
    _json_path = json_path
    if not os.path.exists(json_path):
        _metrics = []
        return
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _metrics = [Metric(**item) for item in data]


def list_metrics(
    keyword: str | None = None,
    department: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> MetricListResponse:
    """分页查询指标，支持按 name/code 模糊搜索和科室精确筛选"""
    filtered = _metrics
    if keyword:
        kw = keyword.lower()
        filtered = [m for m in filtered if kw in m.name.lower() or kw in m.code.lower()]
    if department:
        filtered = [m for m in filtered if m.department == department]
    total = len(filtered)
    start = (page - 1) * page_size
    items = filtered[start:start + page_size]
    return MetricListResponse(items=items, total=total)


def get_metric_by_id(metric_id: str) -> Metric | None:
    """根据 ID 查找单个指标，不存在返回 None"""
    for m in _metrics:
        if m.id == metric_id:
            return m
    return None


async def create_metric(question: str, formula) -> Metric:
    """
    新建指标：生成自增 ID，追加到列表，写回文件
    完善：
        code 、
        department 、
        reference 、
        以上3个字段暂无自动生成，先直接补充吧
    """
    metric = await srge.rule_generate(question, formula) # 先占位
    info = Tools.metric_info_generate(question, formula)
    metric.update(info)

    # 写回文件
    with _lock:
        _metrics.append(metric)
        _save()
    return metric


def update_metric(metric_id: str, data: dict) -> Metric | None:
    """部分更新指标字段，不存在返回 None"""
    with _lock:
        for i, m in enumerate(_metrics):
            if m.id == metric_id:
                updated = m.model_copy(update=data)
                _metrics[i] = updated
                _save()
                return updated
    return None


def delete_metric(metric_id: str) -> bool:
    """删除指标，成功返回 True，不存在返回 False"""
    with _lock:
        for i, m in enumerate(_metrics):
            if m.id == metric_id:
                _metrics.pop(i)
                _save()
                return True
    return False

from utils.meta import generate_meta
def _save() -> None:
    """内部方法：带锁将当前指标列表写回 metrics.json"""
    os.makedirs(os.path.dirname(_json_path), exist_ok=True)
    with open(_json_path, "w", encoding="utf-8") as f:
        json.dump([m.model_dump() for m in _metrics], f, ensure_ascii=False, indent=2)
    meta_data = generate_meta(_metrics)
    # 更新信息
    with open(_meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=2)

def _convert(metric):
    """内部方法：将直接生成的metric转换为规范的Metric对象"""

    current_json = metric
    # 处理 inputs：将 gender 的 input_type 改为 enum
    inputs = []
    for inp in current_json.get("inputs", []):
        new_inp = {
            "input_name": inp.get("input_name"),
            "input_desc": inp.get("input_desc"),
            "input_type": inp.get("input_type")
        }
        # 如果字段名是 gender 且原类型是 str，改为 enum
        if new_inp["input_name"] == "gender" and new_inp["input_type"] == "str":
            new_inp["input_type"] = "enum"
        inputs.append(new_inp)

    # 处理 steps：转换 input_source 中的引用格式
    steps = []
    for step in current_json.get("steps", []):
        new_step = step.copy()  # 浅拷贝，保留原有字段
        # 转换 step_inputs 中的 input_source
        new_step_inputs = []
        for step_inp in step.get("step_inputs", []):
            new_step_inp = step_inp.copy()
            source = new_step_inp.get("input_source", "")
            # 将 $|数字|.field 替换为 $|steps|.数字.field
            if re.match(r'^\$\|\d+\|\.', source):
                new_source = re.sub(r'^\$\|(\d+)\|\.', r'$|steps|.\1.', source)
                new_step_inp["input_source"] = new_source
            new_step_inputs.append(new_step_inp)
        new_step["step_inputs"] = new_step_inputs
        steps.append(new_step)

    # 构建目标对象
    target_obj = {
        "id": None,
        "code": None,
        "name": current_json.get("name"),
        "description": current_json.get("description"),
        "department": None,
        "reference": None,
        "inputs": inputs,
        "output": current_json.get("output"),
        "steps": steps,
        "executableCode": current_json.get("code")  # 原 code 字段映射为 executableCode
    }

    return target_obj

if __name__ == "__main__":
    metric = {
        "name": "creatinine_clearance_calculation_workflow",
        "description": "Calculate creatinine clearance (CrCl) using the Cockcroft-Gault equation, with weight selection based on BMI category using actual, ideal, or adjusted body weight.",
        "inputs": [
            {
                "input_name": "weight_kg",
                "input_desc": "Patient's actual body weight in kg",
                "input_type": "float"
            },
            {
                "input_name": "height_m",
                "input_desc": "Patient's height in meters",
                "input_type": "float"
            },
            {
                "input_name": "height_in",
                "input_desc": "Patient's height in inches",
                "input_type": "float"
            },
            {
                "input_name": "gender",
                "input_desc": "Patient's gender: 'male' or 'female'",
                "input_type": "str"
            },
            {
                "input_name": "age",
                "input_desc": "Patient's age in years",
                "input_type": "int"
            },
            {
                "input_name": "serum_creatinine_mg_dl",
                "input_desc": "Serum creatinine level in mg/dL",
                "input_type": "float"
            }
        ],
        "steps": [
            {
                "step_id": "1",
                "step_name": "bmi_calculation",
                "step_description": "Calculate the patient's Body Mass Index (BMI) using weight in kg and height in meters.",
                "step_inputs": [
                    {
                        "input_name": "weight_kg",
                        "input_desc": "Patient's actual body weight in kg",
                        "input_type": "float",
                        "input_source": "$|inputs|.weight_kg"
                    },
                    {
                        "input_name": "height_m",
                        "input_desc": "Patient's height in meters",
                        "input_type": "float",
                        "input_source": "$|inputs|.height_m"
                    }
                ],
                "step_outputs": [
                    {
                        "output_name": "bmi",
                        "output_desc": "Calculated BMI value",
                        "output_type": "float"
                    }
                ],
                "category": "FormulaCalculation",
                "reason": "This step applies a simple mathematical formula to compute BMI from weight and height, which is a direct numerical calculation without branching.",
                "detail": "BMI = weight_kg / (height_m * height_m)"
            },
            {
                "step_id": "2",
                "step_name": "bmi_classification",
                "step_description": "Classify the patient's BMI into underweight, normal, or overweight/obese categories.",
                "step_inputs": [
                    {
                        "input_name": "bmi",
                        "input_desc": "Calculated BMI value",
                        "input_type": "float",
                        "input_source": "$|1|.bmi"
                    }
                ],
                "step_outputs": [
                    {
                        "output_name": "bmi_category",
                        "output_desc": "BMI category: 'underweight', 'normal', or 'overweight/obese'",
                        "output_type": "str"
                    }
                ],
                "category": "ThresholdMapping",
                "reason": "This step maps a continuous BMI value to discrete categories based on predefined thresholds, which is a classic threshold mapping scenario.",
                "detail": "If BMI < 18.5, category = 'underweight'; else if 18.5 <= BMI <= 24.9, category = 'normal'; else (BMI >= 25), category = 'overweight/obese'."
            },
            {
                "step_id": "3",
                "step_name": "ideal_body_weight_calculation",
                "step_description": "Calculate the patient's Ideal Body Weight (IBW) using the Devine formula based on gender and height in inches.",
                "step_inputs": [
                    {
                        "input_name": "gender",
                        "input_desc": "Patient's gender: 'male' or 'female'",
                        "input_type": "str",
                        "input_source": "$|inputs|.gender"
                    },
                    {
                        "input_name": "height_in",
                        "input_desc": "Patient's height in inches",
                        "input_type": "float",
                        "input_source": "$|inputs|.height_in"
                    }
                ],
                "step_outputs": [
                    {
                        "output_name": "ibw_kg",
                        "output_desc": "Ideal body weight in kg",
                        "output_type": "float"
                    }
                ],
                "category": "FormulaCalculation",
                "reason": "This step computes IBW using a gender-dependent linear formula, which is a straightforward mathematical calculation.",
                "detail": "If gender is 'male': IBW = 50 + 2.3 * (height_in - 60); if gender is 'female': IBW = 45.5 + 2.3 * (height_in - 60)."
            },
            {
                "step_id": "4",
                "step_name": "adjusted_body_weight_calculation",
                "step_description": "Determine the weight to be used in the Cockcroft-Gault equation based on BMI category. Calculate Adjusted Body Weight (ABW) only if needed.",
                "step_inputs": [
                    {
                        "input_name": "bmi_category",
                        "input_desc": "BMI category: 'underweight', 'normal', or 'overweight/obese'",
                        "input_type": "str",
                        "input_source": "$|2|.bmi_category"
                    },
                    {
                        "input_name": "actual_weight_kg",
                        "input_desc": "Patient's actual body weight in kg",
                        "input_type": "float",
                        "input_source": "$|inputs|.weight_kg"
                    },
                    {
                        "input_name": "ibw_kg",
                        "input_desc": "Ideal body weight in kg",
                        "input_type": "float",
                        "input_source": "$|3|.ibw_kg"
                    }
                ],
                "step_outputs": [
                    {
                        "output_name": "weight_to_use_kg",
                        "output_desc": "Weight value to be used in CrCl calculation",
                        "output_type": "float"
                    }
                ],
                "category": "ConditionEvaluation",
                "reason": "This step uses conditional branching based on BMI category to select the appropriate weight, which is a multi-branch condition evaluation with a formula embedded in one branch.",
                "detail": "If bmi_category == 'underweight': weight_to_use = actual_weight_kg; else if bmi_category == 'normal': weight_to_use = min(ibw_kg, actual_weight_kg); else (overweight/obese): ABW = ibw_kg + 0.4 * (actual_weight_kg - ibw_kg), weight_to_use = ABW."
            },
            {
                "step_id": "5",
                "step_name": "creatinine_clearance_calculation",
                "step_description": "Calculate Creatinine Clearance (CrCl) using the Cockcroft-Gault Equation.",
                "step_inputs": [
                    {
                        "input_name": "age",
                        "input_desc": "Patient's age in years",
                        "input_type": "int",
                        "input_source": "$|inputs|.age"
                    },
                    {
                        "input_name": "weight_to_use_kg",
                        "input_desc": "Weight to use in kg (determined from previous step)",
                        "input_type": "float",
                        "input_source": "$|4|.weight_to_use_kg"
                    },
                    {
                        "input_name": "gender",
                        "input_desc": "Patient's gender: 'male' or 'female'",
                        "input_type": "str",
                        "input_source": "$|inputs|.gender"
                    },
                    {
                        "input_name": "serum_creatinine_mg_dl",
                        "input_desc": "Serum creatinine level in mg/dL",
                        "input_type": "float",
                        "input_source": "$|inputs|.serum_creatinine_mg_dl"
                    }
                ],
                "step_outputs": [
                    {
                        "output_name": "crcl_ml_min",
                        "output_desc": "Creatinine clearance in mL/min",
                        "output_type": "float"
                    }
                ],
                "category": "FormulaCalculation",
                "reason": "This step applies the Cockcroft-Gault formula, which is a precise numerical computation with a gender-based coefficient selection, fitting the FormulaCalculation tool.",
                "detail": "gender_coefficient = 1 if gender is 'male', else 0.85; CrCl = ((140 - age) * weight_to_use_kg * gender_coefficient) / (72 * serum_creatinine_mg_dl). Round result to 4 decimal places."
            }
        ],
        "output": {
            "output_name": "crcl_ml_min",
            "output_desc": "Creatinine clearance in mL/min",
            "output_type": "float"
        },
        "code": "def solve(weight_kg, height_m, height_in, gender, age, serum_creatinine_mg_dl):\n    # Step 1: bmi_calculation - Calculate the patient's Body Mass Index (BMI) using weight in kg and height in meters.\n    bmi = weight_kg / (height_m * height_m)\n    yield {\n        \"step_name\": \"bmi_calculation\",\n        \"step_description\": \"Calculate the patient's Body Mass Index (BMI) using weight in kg and height in meters.\",\n        \"step_result\": bmi,\n        \"unit\": \"kg/m^2\"\n    }\n\n    # Step 2: bmi_classification - Classify the patient's BMI into underweight, normal, or overweight/obese categories.\n    if bmi < 18.5:\n        bmi_category = 'underweight'\n    elif 18.5 <= bmi <= 24.9:\n        bmi_category = 'normal'\n    else:\n        bmi_category = 'overweight/obese'\n    yield {\n        \"step_name\": \"bmi_classification\",\n        \"step_description\": \"Classify the patient's BMI into underweight, normal, or overweight/obese categories.\",\n        \"step_result\": bmi_category,\n        \"unit\": None\n    }\n\n    # Step 3: ideal_body_weight_calculation - Calculate the patient's Ideal Body Weight (IBW) using the Devine formula based on gender and height in inches.\n    if gender == 'male':\n        ibw_kg = 50 + 2.3 * (height_in - 60)\n    else:  # female\n        ibw_kg = 45.5 + 2.3 * (height_in - 60)\n    yield {\n        \"step_name\": \"ideal_body_weight_calculation\",\n        \"step_description\": \"Calculate the patient's Ideal Body Weight (IBW) using the Devine formula based on gender and height in inches.\",\n        \"step_result\": ibw_kg,\n        \"unit\": \"kg\"\n    }\n\n    # Step 4: adjusted_body_weight_calculation - Determine the weight to be used in the Cockcroft-Gault equation based on BMI category. Calculate Adjusted Body Weight (ABW) only if needed.\n    if bmi_category == 'underweight':\n        weight_to_use_kg = weight_kg\n    elif bmi_category == 'normal':\n        weight_to_use_kg = min(ibw_kg, weight_kg)\n    else:  # overweight/obese\n        abw_kg = ibw_kg + 0.4 * (weight_kg - ibw_kg)\n        weight_to_use_kg = abw_kg\n    yield {\n        \"step_name\": \"adjusted_body_weight_calculation\",\n        \"step_description\": \"Determine the weight to be used in the Cockcroft-Gault equation based on BMI category. Calculate Adjusted Body Weight (ABW) only if needed.\",\n        \"step_result\": weight_to_use_kg,\n        \"unit\": \"kg\"\n    }\n\n    # Step 5: creatinine_clearance_calculation - Calculate Creatinine Clearance (CrCl) using the Cockcroft-Gault Equation.\n    gender_coefficient = 1 if gender == 'male' else 0.85\n    crcl_ml_min = ((140 - age) * weight_to_use_kg * gender_coefficient) / (72 * serum_creatinine_mg_dl)\n    crcl_ml_min = round(crcl_ml_min, 4)\n    yield {\n        \"step_name\": \"creatinine_clearance_calculation\",\n        \"step_description\": \"Calculate Creatinine Clearance (CrCl) using the Cockcroft-Gault Equation.\",\n        \"step_result\": crcl_ml_min,\n        \"unit\": \"mL/min\"\n    }\n\n    return crcl_ml_min"
    }

    converted_metric = _convert(metric)

    with open("converted_metric.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(converted_metric, ensure_ascii=False, indent=4))