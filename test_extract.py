import asyncio
import json

from services.core import srge


# ── 测试数据 ──

# 模拟 workflow，包含 inputs 参数定义（与 extracted_param 结构化输出格式对应）
workflow = {
    "inputs": [
        {"input_name": "age", "input_desc": "Patient's age in years", "input_type": "int"},
        {"input_name": "gender", "input_desc": "Patient's gender: 'male' or 'female'", "input_type": "string"},
        {"input_name": "weight_kg", "input_desc": "Patient's actual body weight in kg", "input_type": "float"},
        {"input_name": "height_cm", "input_desc": "Patient's height in cm", "input_type": "float"},
        {"input_name": "serum_creatinine", "input_desc": "Serum creatinine level in mg/dL", "input_type": "float"},
        {"input_name": "diabetes", "input_desc": "Whether patient has diabetes (yes/no)", "input_type": "string"},
        {"input_name": "smoking", "input_desc": "Whether patient is a smoker (yes/no)", "input_type": "string"},
    ]
}

patient_info = """
Patient is a 58-year-old male with a history of type 2 diabetes and hypertension.
Height: 172 cm, Weight: 85 kg.
Blood pressure: 145/90 mmHg.
Serum creatinine: 1.3 mg/dL.
Fasting blood glucose: 150 mg/dL.
HbA1c: 7.8%.
The patient is a current smoker (20 pack-years).
"""


async def main():
    print("=" * 60)
    print("【参数抽取测试】extract_parameters")
    print("=" * 60)
    print("【参数定义 (workflow.inputs)】")
    for inp in workflow["inputs"]:
        print(f"  - {inp['input_name']} ({inp['input_type']}): {inp['input_desc']}")
    print("=" * 60)
    print("【病人信息】")
    print(patient_info.strip())
    print("=" * 60)

    result = await srge.extract_parameters(
        workflow=workflow,
        patient_info=patient_info.strip(),
    )

    print("\n【抽取结果】")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 60)

    # 验证抽取结果
    print("【验证】")
    expected_params = {inp["input_name"] for inp in workflow["inputs"]}
    extracted_params = {item["name"] for item in result}
    print(f"期望参数数量: {len(expected_params)}, 实际抽取数量: {len(extracted_params)}")

    missing = expected_params - extracted_params
    extra = extracted_params - expected_params

    if missing:
        print(f"⚠ 缺失参数: {missing}")
    if extra:
        print(f"⚠ 多余参数: {extra}")

    all_found = True
    for item in result:
        name = item["name"]
        raw = item.get("rawValue", "")
        norm = item.get("normalizedValue")
        conf = item.get("confidence", 0)
        status = "✓" if raw and norm is not None else "✗"
        if status == "✗":
            all_found = False
        print(f"  {status} {name}: rawValue='{raw}', normalizedValue={norm}, confidence={conf}")

    print("=" * 60)
    if not missing and not extra and all_found:
        print("✅ 参数抽取测试通过：所有参数均已成功抽取")
    else:
        print("❌ 参数抽取测试未完全通过，请检查上述标记")


if __name__ == "__main__":
    asyncio.run(main())
