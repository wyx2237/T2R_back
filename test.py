import asyncio
from models.metric import Metric, WorkflowStep
from services.core import srge
from services.executor import execute

import json

patient_info = """
患者，女，62岁，因反复咳嗽、咳痰两周就诊，既往有慢阻肺病史，吸烟30年，每天一包，无药物过敏史，身高1.58米，体重56kg，血压128/84 mmHg，心率76次/分，体温36.5℃，空腹血糖5.3 mmol/L，低密度脂蛋白2.8 mmol/L。
"""

workflow = {
    "id": "metric_002",
    "code": "BMI-001",
    "name": "Body Mass Index (BMI)",
    "description": "Calculate Body Mass Index based on weight and height using the standard formula (weight in kg divided by square of height in meters).",
    "department": "General Medicine / Nutrition",
    "reference": "WHO BMI classification",
    "inputs": [
      { "input_name": "Weight", "input_desc": "Body weight in kilograms", "input_type": "float" },
      { "input_name": "Height", "input_desc": "Body height in meters", "input_type": "float" },
      { "input_name": "HeightUnit", "input_desc": "Unit of height (m or cm)", "input_type": "enum", "optional": True }
    ],
    "output": {
      "output_name": "BMI",
      "output_desc": "Calculated Body Mass Index",
      "output_type": "float"
    },
    "steps": [
      {
        "step_id": "1",
        "step_name": "normalize_height_unit",
        "step_description": "Convert height to meters if provided in centimeters.",
        "step_inputs": [
          { "input_name": "Height", "input_desc": "Body height value", "input_type": "float", "input_source": "$|inputs|.Height" },
          { "input_name": "HeightUnit", "input_desc": "Unit of height (m or cm)", "input_type": "enum", "input_source": "$|inputs|.HeightUnit", "optional": True }
        ],
        "step_outputs": [
          { "output_name": "Height_m", "output_desc": "Height in meters", "output_type": "float" }
        ],
        "category": "unit_conversion",
        "reason": "BMI formula requires height in meters. Input may be provided in centimeters.",
        "detail": "If HeightUnit is 'cm' or height > 3 (assuming unlikely >3m), divide by 100. Otherwise keep as meters. Default assumes meters if unit missing."
      },
      {
        "step_id": "2",
        "step_name": "compute_bmi",
        "step_description": "Compute BMI = weight (kg) / (height in meters)^2.",
        "step_inputs": [
          { "input_name": "Weight", "input_desc": "Body weight in kg", "input_type": "float", "input_source": "$|inputs|.Weight" },
          { "input_name": "Height_m", "input_desc": "Height in meters", "input_type": "float", "input_source": "$|steps|.1.Height_m" }
        ],
        "step_outputs": [
          { "output_name": "BMI", "output_desc": "Body Mass Index value", "output_type": "float" }
        ],
        "category": "formula_calculation",
        "reason": "Standard BMI calculation based on weight and height.",
        "detail": "BMI = Weight / (Height_m ^ 2). Result rounded to one decimal place."
      },
      {
        "step_id": "3",
        "step_name": "classify_bmi_category",
        "step_description": "Classify BMI according to WHO standards.",
        "step_inputs": [
          { "input_name": "BMI", "input_desc": "BMI value", "input_type": "float", "input_source": "$|steps|.2.BMI" }
        ],
        "step_outputs": [
          { "output_name": "BMICategory", "output_desc": "Weight status category", "output_type": "string" }
        ],
        "category": "condition_evaluation",
        "reason": "Clinical and nutritional assessment requires BMI category for management.",
        "detail": "Underweight: <18.5; Normal weight: 18.5-24.9; Overweight: 25-29.9; Obesity Class I: 30-34.9; Obesity Class II: 35-39.9; Obesity Class III: ≥40."
      }
    ],
    "executableCode": "def solve(Weight, Height, HeightUnit=None):\n    # Step 1: Normalize height to meters\n    if HeightUnit == \"cm\" or (HeightUnit is None and Height > 3):\n        # Assume >3 meters unlikely, so treat as cm\n        Height_m = Height / 100.0\n    else:\n        Height_m = Height\n    yield {\"step_name\": \"normalize_height_unit\", \"step_result\": Height_m, \"unit\": \"m\"}\n\n    # Step 2: Compute BMI\n    bmi = Weight / (Height_m ** 2)\n    bmi = round(bmi, 1)\n    yield {\"step_name\": \"compute_bmi\", \"step_result\": bmi, \"unit\": \"kg/m²\"}\n\n    # Step 3: Classify BMI category\n    if bmi < 18.5:\n        category = \"Underweight\"\n    elif bmi < 25:\n        category = \"Normal weight\"\n    elif bmi < 30:\n        category = \"Overweight\"\n    elif bmi < 35:\n        category = \"Obesity Class I\"\n    elif bmi < 40:\n        category = \"Obesity Class II\"\n    else:\n        category = \"Obesity Class III\"\n    yield {\"step_name\": \"classify_bmi_category\", \"step_result\": category, \"unit\": None}\n\n    return bmi"
}

metric = Metric(**workflow)
# print(metric)

# result = asyncio.run(srge.extract_parameters(workflow=workflow, patient_info=patient_info))
# print(result)
result = asyncio.run(execute(metric=metric, raw_text=patient_info))
print(json.dumps(result.model_dump(), ensure_ascii=False, indent=4))