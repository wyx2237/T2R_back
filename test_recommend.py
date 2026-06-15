import asyncio
import json

from services.core import recommand
from utils.regex_tools import regex_json_doc


# ── 测试数据 ──

k = 3

raw_text = """
Patient is a 58-year-old male with a history of type 2 diabetes and hypertension.
Height: 172 cm, Weight: 85 kg.
Blood pressure: 145/90 mmHg.
Serum creatinine: 1.3 mg/dL.
Fasting blood glucose: 150 mg/dL.
HbA1c: 7.8%.
Total cholesterol: 210 mg/dL, LDL: 135 mg/dL, HDL: 40 mg/dL.
The patient is a current smoker (20 pack-years).
"""

available_metrics = [
    {
        "id": "BMI",
        "code": "BMI",
        "department": "General",
        "reference": "WHO BMI classification",
        "name": "身体质量指数 (BMI)",
        "description": "评估体重是否在健康范围内，计算公式：体重(kg) / 身高(m)^2",
        "inputs": [
            {"input_name": "height_cm", "input_desc": "身高(cm)", "input_type": "float"},
            {"input_name": "weight_kg", "input_desc": "体重(kg)", "input_type": "float"},
        ],
        "output": {"output_name": "bmi", "output_desc": "BMI值", "output_type": "float"},
        "steps": [],
        "executableCode": "",
    },
    {
        "id": "BSA",
        "code": "BSA",
        "department": "General",
        "reference": "Mosteller formula",
        "name": "体表面积 (BSA)",
        "description": "计算体表面积，用于药物剂量调整",
        "inputs": [
            {"input_name": "height_cm", "input_desc": "身高(cm)", "input_type": "float"},
            {"input_name": "weight_kg", "input_desc": "体重(kg)", "input_type": "float"},
        ],
        "output": {"output_name": "bsa", "output_desc": "体表面积(m²)", "output_type": "float"},
        "steps": [],
        "executableCode": "",
    },
    {
        "id": "eGFR",
        "code": "eGFR",
        "department": "Nephrology",
        "reference": "CKD-EPI formula",
        "name": "估算肾小球滤过率 (eGFR)",
        "description": "评估肾功能，用于慢性肾病分期",
        "inputs": [
            {"input_name": "serum_creatinine", "input_desc": "血清肌酐(mg/dL)", "input_type": "float"},
            {"input_name": "age", "input_desc": "年龄", "input_type": "int"},
            {"input_name": "gender", "input_desc": "性别（male/female）", "input_type": "string"},
        ],
        "output": {"output_name": "egfr", "output_desc": "eGFR(mL/min/1.73m²)", "output_type": "float"},
        "steps": [],
        "executableCode": "",
    },
    {
        "id": "MAP",
        "code": "MAP",
        "department": "Cardiology",
        "reference": "Mean Arterial Pressure formula",
        "name": "平均动脉压 (MAP)",
        "description": "计算平均动脉压，评估器官灌注情况",
        "inputs": [
            {"input_name": "sbp", "input_desc": "收缩压(mmHg)", "input_type": "float"},
            {"input_name": "dbp", "input_desc": "舒张压(mmHg)", "input_type": "float"},
        ],
        "output": {"output_name": "map", "output_desc": "平均动脉压(mmHg)", "output_type": "float"},
        "steps": [],
        "executableCode": "",
    },
    {
        "id": "ASCVD",
        "code": "ASCVD",
        "department": "Cardiology",
        "reference": "ACC/AHA ASCVD Risk Estimator",
        "name": "ASCVD 10年风险评分",
        "description": "评估未来10年动脉粥样硬化性心血管疾病风险",
        "inputs": [
            {"input_name": "age", "input_desc": "年龄", "input_type": "int"},
            {"input_name": "gender", "input_desc": "性别（male/female）", "input_type": "string"},
            {"input_name": "total_cholesterol", "input_desc": "总胆固醇(mg/dL)", "input_type": "float"},
            {"input_name": "hdl", "input_desc": "HDL胆固醇(mg/dL)", "input_type": "float"},
            {"input_name": "sbp", "input_desc": "收缩压(mmHg)", "input_type": "float"},
            {"input_name": "smoking", "input_desc": "是否吸烟（yes/no）", "input_type": "string"},
            {"input_name": "diabetes", "input_desc": "是否糖尿病（yes/no）", "input_type": "string"},
        ],
        "output": {"output_name": "ascvd_risk", "output_desc": "10年ASCVD风险(%)", "output_type": "float"},
        "steps": [],
        "executableCode": "",
    },
    {
        "id": "CHADS2VASc",
        "code": "CHADS2VASc",
        "department": "Cardiology",
        "reference": "CHA2DS2-VASc score for atrial fibrillation",
        "name": "CHA2DS2-VASc 卒中风险评分",
        "description": "评估房颤患者卒中风险，指导抗凝治疗",
        "inputs": [
            {"input_name": "age", "input_desc": "年龄", "input_type": "int"},
            {"input_name": "gender", "input_desc": "性别（male/female）", "input_type": "string"},
            {"input_name": "hypertension", "input_desc": "是否高血压（yes/no）", "input_type": "string"},
            {"input_name": "diabetes", "input_desc": "是否糖尿病（yes/no）", "input_type": "string"},
            {"input_name": "heart_failure", "input_desc": "是否心衰（yes/no）", "input_type": "string"},
        ],
        "output": {"output_name": "chads2vasc", "output_desc": "CHA2DS2-VASc评分", "output_type": "int"},
        "steps": [],
        "executableCode": "",
    },
    {
        "id": "LDL_GOAL",
        "code": "LDL_GOAL",
        "department": "Cardiology",
        "reference": "ATP III Guidelines",
        "name": "LDL目标值评估",
        "description": "根据危险分层确定LDL-C控制目标",
        "inputs": [
            {"input_name": "ldl", "input_desc": "LDL胆固醇(mg/dL)", "input_type": "float"},
            {"input_name": "diabetes", "input_desc": "是否糖尿病（yes/no）", "input_type": "string"},
            {"input_name": "hypertension", "input_desc": "是否高血压（yes/no）", "input_type": "string"},
            {"input_name": "smoking", "input_desc": "是否吸烟（yes/no）", "input_type": "string"},
            {"input_name": "age", "input_desc": "年龄", "input_type": "int"},
            {"input_name": "gender", "input_desc": "性别（male/female）", "input_type": "string"},
        ],
        "output": {"output_name": "ldl_goal", "output_desc": "LDL目标值(mg/dL)", "output_type": "float"},
        "steps": [],
        "executableCode": "",
    },
]


async def main():
    print("=" * 60)
    print("【病人信息】")
    print(raw_text.strip())
    print("=" * 60)
    print(f"【备选指标库】共 {len(available_metrics)} 个指标")
    for m in available_metrics:
        params = [inp["input_name"] for inp in m["inputs"]]
        print(f"  - {m['id']}: {m['name']} | 所需参数: {params}")
    print("=" * 60)
    print(f"【推荐数量】k = {k}")
    print("=" * 60)

    result = await recommand.recommend(
        raw_text=raw_text.strip(),
        available_metrics=json.dumps(available_metrics, ensure_ascii=False),
        k=k,
    )

    print("\n【推荐结果】")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 60)

    # 验证推荐数量
    recommended = [r for r in result if r.get("recommend")]
    print(f"实际推荐数量: {len(recommended)} / 预期: {k}")
    for r in recommended:
        print(f"  ✓ {r.get('indicatorName')} ({r.get('scoreLabel')})")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())