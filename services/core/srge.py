# text2rule 方法
import sys
sys.path.append("/root/local/BIYELUNWEN/KAITI/DEMO/T2R_back")

from services.core.Agents import *
from utils.general_tools import get_result_content
from utils.regex_tools import regex_json, regex_json_doc, regex_python

import os
import math
import json
import inspect
import datetime

MAX_RETRY_TIMES = 3
# 步骤拆解
async def question_decomposition(patient_info:str, question:str, calculator:dict, wo=False):
    all_input = f"【待计算问题】：\n计算目标：{calculator.get('question')}\n详细计算方法：{calculator.get('formula')}"
    try_times = 0
    while try_times < MAX_RETRY_TIMES:
        try:
            qd_agent = get_QuestionDecomposer()
            result = await qd_agent.run(task=all_input)

            print(f"【qd result】: \n{result}")  # 打印qd结果
            answer = get_result_content(result)
            print(f"【qd answer】: \n{answer}")
            steps = regex_json_doc(answer)
            print(f"【qd steps str】: \n{steps}")
            steps = json.loads(steps)  # 将字符串转换为JSON对象
            print(f"【qd steps json】: \n{steps}")
            return steps
        except Exception as e:
            print(f"【qd error】: \n{e}")
            try_times += 1
            print(f"【qd retry】: \n{try_times}")
    raise Exception(f"【qd error】: \n{e}，已重试{try_times}次，无法继续计算。")

# 流程定义
async def workflow_modeling(patient_info:str, question:str, calculator:dict, steps:list):
    all_input = f"【待计算问题】：\n{calculator.get('question')}\n详细信息：{calculator.get('formula')}\n\n【规范化步骤表示】：\n{steps}"
    wm_agent = get_WorkflowModeler()
    result = await wm_agent.run(task=all_input)
    answer = get_result_content(result)
    print(f"【wm answer】: \n{answer}")
    worflow = regex_json(answer)
    workflow = json.loads(worflow)  # 将字符串转换为JSON对象
    print(f"【wm workflow】: \n{workflow}")
    return workflow
    

# 依赖验证
"""
context = {
    "raw input": ["param1", "param2"]
    "step1": ["param1", ...]
    ...
}
"""
# dv_agent = get_DependencyVerifier()
async def dependency_verification(steps:list[dict], context:str):
    """
    遍历每一个step，检查输入依赖是否正确——从原初输入或者前置步骤的结果获取当前步骤的输入
    Params：
        steps：步骤序列 从属于 workflow
        context：上下文字典，传入时只包含原初输入raw input，遍历中逐步添加各个步骤的结果丰富内容
        workflow：wm阶段生成的流程定义，在本阶段验证依赖、添加信息
    """
    updated_steps = []
    for idx, step in enumerate(steps):
        all_input = f"【当前步骤】：\n{step}\n\n【上下文字典】context：\n{context}"
        dv_agent = get_DependencyVerifier()
        result = await dv_agent.run(task=all_input)
        answer = get_result_content(result)
        print(f"【dv answer】: \n{answer}")
        input_source_dict = regex_json(answer)
        input_source_dict = json.loads(input_source_dict)  # 将字符串转换为JSON对象
        print(f"【dv input_source_dict】: \n{input_source_dict}")
        
        # 更新上下文字典，添加当前步骤的输入来源
        context[f"step{idx+1}"] = [ item["output_name"] for item in step.get("step_outputs", [])]
        for item in step.get("step_inputs", []):
            name = item["input_name"]
            source = input_source_dict.get(name, [])  # 获取当前步骤的输入来源
            item["input_source"] = source
        updated_steps.append(step)
    print(f"【dv updated_steps】: \n{updated_steps}")  # 更新后的步骤序列，包含输入来源信息
    return updated_steps


# 代码合成
# cg_agent = get_CodeGenerator()
async def code_generation(workflow:dict):
    all_input = f"【计算流程】：\n{workflow}"
    cg_agent = get_CodeGenerator()
    result = await cg_agent.run(task=all_input)
    answer = get_result_content(result)
    print(f"【cg answer】: \n{answer}")
    code = regex_python(answer)
    print(f"【cg code】: \n{code}")
    return code

## 计算阶段
# 参数抽取
async def extract_parameters(workflow:dict, patient_info:str, question:str=None):
    """
    根据 workflow.inputs，从patient_info中抽取参数。
    最大重试 MAX_RETRY_TIMES 次。
    """
    all_input = f"【参数定义】：\n{workflow.get('inputs', [])}\n\n【病人信息】：\n{question}\n{patient_info}"
    ex_agent = get_StructuredExtractor()

    try_times = 0
    while try_times < MAX_RETRY_TIMES:
        try:
            result = await ex_agent.run(task=all_input)
            answer = get_result_content(result)
            answer = _modify_regex(answer, "json")
            print(f"【ex answer】: \n{answer}")
            result = regex_json(answer)
            print(f"【ex regex answer】: \n{result}")
            input_params = json.loads(result)
            print(f"【ex input_params】: \n{input_params}")
            return input_params
        except Exception as e:
            try_times += 1
            print(f"【ex error】: {e}")
            print(f"【ex retry】: {try_times}/{MAX_RETRY_TIMES}")
    raise Exception(f"【ex error】: 参数抽取失败，已重试 {MAX_RETRY_TIMES} 次，无法完成抽取。")

# 代码执行
# 创建代码沙盒执行生成的代码
def execute_code(code: str, input_params: dict) -> dict:
    # print(f"type(code): {type(code)}")
    # print(f"code: \n{code}")
    print(f"【code】: \n{code}")
    # 编译代码
    compiled_code = compile(source=code, filename="", mode="exec")

    # 独立命名空间执行，防止污染
    local_namespace = {}
    globals = {
        "__builtins__": __builtins__,
        "math": math,
        "datetime": datetime,
    }
    exec(compiled_code, globals, local_namespace)

    # 获取 solve 函数
    solve = local_namespace["solve"]

    # 获取函数参数名（可选，用于调试）
    sig = inspect.signature(solve)
    params = list(sig.parameters.keys())
    print("函数参数列表:", params)

    # 调用 solve，得到生成器
    gen = solve(**input_params)

    steps = []          # 收集每一步 yield 的结果
    final_value = None  # 最终 return 的值

    try:
        while True:
            step_output = next(gen)
            steps.append(step_output)
            # print(step_output)   # 保留原有打印行为
    except StopIteration as e:
        # 获取 return 的值（Python 3.3+）
        final_value = e.value if hasattr(e, 'value') else None
        # print("最终结果:", final_value)

    # 返回包含中间步骤和最终结果的字典
    return {
        "steps": steps,
        "final_value": final_value
    }

# TEMP_WORKFLOWS_PATH = "/root/local/BIYELUNWEN/KAITI/SRGE/method/workflows/CHMedcalc"
# TEMP_WORKFLOWS_PATH = "/root/local/BIYELUNWEN/KAITI/SRGE/method/workflows/medcalc"
async def rule_generate(patient_info:str="", question:str="", formula:str="", calculator:dict={}, wo=False):
    # file_name = f"{calculator.get('calculator id')}.json"
    # if wo:
    #     file_name = f"{calculator.get('calculator id')}_wo.json"
    # workflow_path = os.path.join(TEMP_WORKFLOWS_PATH, file_name)
    # print(f"workflow_path: {workflow_path}")
    # if os.path.exists(workflow_path): # 已存在不重新生成
    #     with open(workflow_path, "r", encoding="utf-8") as f:
    #         workflow = json.loads(f.read())
    #         print("【workflow已存在，直接返回workflow】")  # 已存在直接返回workflow
    #         return workflow
    calculator = {
        "question": question,
        "formula": formula
    }
    # stage1 步骤拆解
    steps = await question_decomposition(patient_info, question, calculator, wo=wo)
    # stage2 流程定义
    workflow = await workflow_modeling(patient_info, question, calculator, steps)
    # stage3 依赖验证
    raw_input = [item["input_name"] for item in workflow.get("inputs")]
    context = {"raw input": raw_input}  # 原初输入
    updated_steps = await dependency_verification(steps=workflow.get("steps", []), context=context)
    workflow["steps"] = updated_steps  # 更新后的步骤序列，包含输入来源信息
    # stage4 代码合成
    code = await code_generation(workflow)
    workflow["code"] = code

    # with open(workflow_path, "w", encoding="utf-8") as f:
    #     f.write(json.dumps(workflow, ensure_ascii=False, indent=4))

    return workflow


async def srge_main(patient_info:str, question:str, calculator:dict):
    workflow = await rule_generate(patient_info, question, calculator)
    input_params = await extract_parameters(workflow=workflow, patient_info=patient_info, question=question)  # 提取参数
    cal_result = execute_code(code=workflow.get("code"), input_params=input_params)
    print(f"【计算结果 cal_result】：\n{cal_result}")
    final_value = cal_result.get("final_value")
    return input_params, final_value

async def calculate(workflow, patient_info):
    input_params = await extract_parameters(workflow=workflow, patient_info=patient_info)  # 提取参数
    # cal_result = execute_code(code=workflow.get("code"), input_params=input_params)
    cal_result = execute_code(code=workflow.get("executableCode"), input_params=input_params)
    print(f"【计算结果 cal_result】：\n{cal_result}")
    final_result = cal_result.get("final_value")
    return input_params, cal_result


if __name__ == "__main__":
    # patient_info = "一名35岁男性，身高178cm，体重70kg，血压140/90mmHg。"
    # question = "计算患者BMI值"
    # calculator = {"formula": "BMI计算公式：BMI = 体重（kg）/身高（m）^2"}
    # asyncio.run(srge_main(patient_info, question, calculator))
    test_code = r"""
import math

def solve(weight_kg, height_cm):
    # Step 1: 计算体重的0.5378次方
    weight_exponent = math.pow(weight_kg, 0.5378)
    yield {
        "step_name": "calculate_weight_exponent",
        "step_description": "计算体重的0.5378次方，根据Haycock公式进行指数运算。",
        "step_result": weight_exponent,
        "unit": None
    }

    # Step 2: 计算身高的0.3964次方
    height_exponent = math.pow(height_cm, 0.3964)
    yield {
        "step_name": "calculate_height_exponent",
        "step_description": "计算身高的0.3964次方，根据Haycock公式进行指数运算。",
        "step_result": height_exponent,
        "unit": None
    }

    # Step 3: 将体重和身高的指数结果相乘
    product_of_exponents = weight_exponent * height_exponent
    yield {
        "step_name": "multiply_weight_and_height_exponents",
        "step_description": "将体重和身高指数结果相乘，得到中间乘积值。",
        "step_result": product_of_exponents,
        "unit": None
    }

    # Step 4: 将乘积乘以系数0.024265，得到最终体表面积（BSA）
    bsa_result = product_of_exponents * 0.024265
    yield {
        "step_name": "multiply_by_coefficient",
        "step_description": "将乘积与系数0.024265相乘，计算最终的体表面积（BSA）。",
        "step_result": bsa_result,
        "unit": "m²"
    }

    return bsa_result
"""
    execute_code(code=test_code, input_params={"weight_kg": 70, "height_cm": 178})

def _modify_regex(text:str, keyword:str):
    mark = f"</{keyword}>"
    if not text.endswith(mark):
        text += "\n" + mark
    return text