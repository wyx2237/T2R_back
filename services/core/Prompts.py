import json

with open("data/tools.json", "r") as f:
    AtomicToolTemplates = json.loads(f.read())

# 问题拆解阶段的提示词
# 需要的输入包含【计算问题】

QUESTION_DECOMPOSITION_PROMPT = """
### 任务说明
你是一个医学领域的计算问题分析专家，你需要对给出的【待计算问题】进行分析和必要的任务拆分，输出若干个独立的子步骤
- 我会为你提供【待计算问题】的计算目标（最终值） + 详细计算方法，请严格遵循计算目标，并参照详细计算方法进行分析。
- 如果是能够一步解决的问题，避免不必要的拆分（例如对于一个具备语义的简单数学公式，不应该再拆分为若干无意义的琐碎步骤）
- 在拆解成多个步骤的过程中，你需要从【工具模板清单】中选出最贴合当前步骤的工具模板，作为当前步骤的所属类型-Category，并且需要给出选取该工具模板的理由Reasoning。
- 对于每个符合的特定工具模版的步骤，请列出我要求的【步骤信息】, 并且你需要保证这些步骤能够组合为一个完整的计算流程，给出【步骤组合的流程示意】。
- 拆解的步骤数量不应超过6个，降低复杂度。
- 禁止出现 “从病人信息中获取XX数据”类型的步骤，这不是你需要关注的事情。
- 最后，反思当前的步骤先后顺序是否存在问题，并进行相应的调整，确保步骤组合的合理性。


### 输出格式
# 输出1 步骤列表 
```json
[ 步骤1, 步骤2, ...] 
```



### 输出示例
```json
[
    {
        "Name": "Name1", # 步骤的名称，根据你拆解的步骤自由生成，例如 BMI Calculattion, Cofficient Selection, ...
        "Description": "Description1", # 步骤的详细描述
        "Inputs": [ 
            {
                "input_name": "input_name1",
                "input_desc": "input_desc1",
                "input_type": "input_type1"
            }
        ],
        "Outputs": [
            {
                "output_name": "output_name1",
                "output_desc": "output_desc1",
                "output_type": "output_type1"
            }
        ],
        "Detail": "Detail1...", # 该步骤的所有的、完整的计算方法细节（计算公式 或者 计分规则等）
        "Category": "FormulaCalculation", # 该字段赋值为你选择的工具模板的 Name，务必保持一致，驼峰命名法例如
        "Reasoning": "Reasoning1..." # 你选择这个工具模版的原因和解释
    },
    ...
]
```

### Inputs参数说明
- 参数的取值尽可能简单，例如一个具体数值（或具体日期）、表示有或无的布尔值、数量有限的简单字符串变量（英文）作为枚举值
- 例如：对于身高、体重等参数，用具体数值；对于是否患有某种疾病、是否表现某种症状，用`疾病或症状名称:布尔值`的方式等

### 重要提示
- 严格按照【输出格式】，仿照【输出示例】输出结果，禁止输出多余内容。
- 避免不必要的步骤拆分（例如对于一个具备语义的简单公式，不应该再拆分为若干无意义的琐碎步骤），
- Detail 字段必须包含当前步骤的所有的计算细节、计分规则，涵盖定义中的所有情况
- 输出的结果中，步骤数量不能超过6个 ！！
- Please answer with English

### 【工具模板清单】
{}
"""
QUESTION_DECOMPOSITION_PROMPT_ALL = QUESTION_DECOMPOSITION_PROMPT + "\n" + json.dumps(AtomicToolTemplates, ensure_ascii=False, indent=4)
# 流程定义阶段的提示词
# 需要的输入包含【计算问题】和【规范化步骤表示】

QUESTION_DECOMPOSITION_WO_ATOMIC = """
### 任务说明
你是一个医学领域的计算问题分析专家，你需要对给出的【待计算问题】进行分析和必要的任务拆分，输出若干个独立的子步骤
- 我会为你提供【待计算问题】的计算目标（最终值） + 详细计算方法，请严格遵循计算目标，并参照详细计算方法进行分析。
- 如果是能够一步解决的问题，避免不必要的拆分（例如对于一个具备语义的简单数学公式，不应该再拆分为若干无意义的琐碎步骤）
- 对于每个符合的特定工具模版的步骤，请列出我要求的【步骤信息】, 并且你需要保证这些步骤能够组合为一个完整的计算流程，给出【步骤组合的流程示意】。
- 拆解的步骤数量不应超过6个，降低复杂度。
- 禁止出现 “从病人信息中获取XX数据”类型的步骤，这不是你需要关注的事情。
- 最后，反思当前的步骤先后顺序是否存在问题，并进行相应的调整，确保步骤组合的合理性。


### 输出格式
# 输出1 步骤列表
```json
[ 步骤1, 步骤2, ...] 
```



### 输出示例
```json
[
    {
        "Name": "Name1", # 步骤的名称，根据你拆解的步骤自由生成，例如 BMI Calculattion, Cofficient Selection, ...
        "Description": "Description1", # 步骤的详细描述
        "Inputs": [ 
            {
                "input_name": "input_name1",
                "input_desc": "input_desc1",
                "input_type": "input_type1"
            }
        ],
        "Outputs": [
            {
                "output_name": "output_name1",
                "output_desc": "output_desc1",
                "output_type": "output_type1"
            }
        ],
        "Detail": "Detail1...", # 该步骤的所有的、完整的计算方法细节（计算公式 或者 计分规则等）
    },
    ...
]
```

### Inputs参数说明
- 参数的取值尽可能简单，例如一个具体数值（或具体日期）、表示有或无的布尔值、数量有限的简单字符串变量（英文）作为枚举值
- 例如：对于身高、体重等参数，用具体数值；对于是否患有某种疾病、是否表现某种症状，用`疾病或症状名称:布尔值`的方式等

### 重要提示
- 严格按照【输出格式】，仿照【输出示例】输出结果，禁止输出多余内容。
- 避免不必要的步骤拆分（例如对于一个具备语义的简单公式，不应该再拆分为若干无意义的琐碎步骤），
- Detail 字段必须包含当前步骤的所有的计算细节、计分规则，涵盖定义中的所有情况
- 输出的结果中，步骤数量不能超过6个 ！！
- Please answer with English
"""



WORKFLOW_MODELING_PROMPT = """
### 任务说明
- 你是一个医学领域的计算问题分析专家。
- 你需要根据我给出的【计算问题】以及根据该【计算问题】生成的一组【规范化步骤表示】，组合成一个能够完成该计算问题的完整输入输出流程表示，并按照【输出格式】输出。  
- 最后请全部以英文输出结果，禁止出现任何中文字符。**（即输出的 JSON 内容使用英文）

### 输出格式
# 以 JSON 格式输出，以xml标签对<json></json>封装，禁止使用```json ```的标记来封装
<json>
{
    "name": "计算流程名称（字符串）",
    "description": "计算流程的详细描述（字符串）",
    "inputs": [
        {
            "input_name": "输入参数名称，只允许小写字母、数字、下划线组成，且必须以字母开头，蛇形命名法",
            "input_desc": "输入参数的完整描述，对于存在计量单位的参数请明确说明单位；对于枚举值的字符串参数，请列出所有枚举值，应简洁清晰",
            "input_type": "数据类型（如 float, int, str, bool）"
        }
    ],
    "steps": [
        {
            "step_id": "步骤编号，从1开始递增，字符串类型（如 '1', '2'）",
            "step_name": "步骤名称（字符串）",
            "step_description": "步骤的简要描述（字符串）",
            "step_inputs": [
                {
                    "input_name": "输入参数名称（蛇形命名法）",
                    "input_desc": "输入参数描述，包括单位或枚举值",
                    "input_type": "数据类型"
                }
            ],
            "step_outputs": [
                {
                    "output_name": "输出参数名称（蛇形命名法）",
                    "output_desc": "输出参数描述",
                    "output_type": "数据类型"
                }
            ],
            "category": "所属类别（工具模板名称），驼峰命名法",
            "reason": "归类原因——解释为什么把这个步骤归类到这一工具模板下",
            "detail": "步骤详细计算过程（字符串）"
        }
    ],
    "output": {
        "output_name": "最终输出参数名称（蛇形命名法）",
        "output_desc": "最终输出参数描述",
        "output_type": "数据类型",
        "output_unit": "输出值的计量单位, 没有单位则null"
    }
}
</json>

### 输出示例
<json>
{
    "name": "bmi_calculation_workflow",
    "description": "根据体重和身高计算身体质量指数（BMI）",
    "inputs": [
        {
            "input_name": "weight_kg",
            "input_desc": "体重，单位为千克",
            "input_type": "float"
        },
        {
            "input_name": "height_m",
            "input_desc": "身高，单位为米",
            "input_type": "float"
        }
    ],
    "steps": [
        {
            "step_id": "1",
            "step_name": "compute_bmi",
            "step_description": "BMI = 体重(kg) / 身高(m)^2",
            "step_inputs": [
                {
                    "input_name": "weight_kg",
                    "input_desc": "体重（千克）",
                    "input_type": "float"
                },
                {
                    "input_name": "height_m",
                    "input_desc": "身高（米）",
                    "input_type": "float"
                }
            ],
            "step_outputs": [
                {
                    "output_name": "bmi_value",
                    "output_desc": "计算得到的 BMI 值",
                    "output_type": "float"
                }
            ],
            "category": "FormulaCalculation", # 驼峰命名法
            "reason": "BMI 计算属于基本的人体测量学指标，使用体重和身高两个参数。",
            "detail": "将体重（千克）除以身高（米）的平方。"
        }
    ],
    "output": {
        "output_name": "bmi_value",
        "output_desc": "最终的 BMI 结果",
        "output_type": "float"
        "output_unit": "kg/m^2"
    }
}
</json>

### 重要说明
- 步骤的数量与提供的【规范化步骤表示】列表中的步骤数量保持一致，禁止再做拆分
- 生成计算流程时，请仔细思考并确认：每一个计算步骤的输入参数、输出参数是否合理，是否能够完成该步骤的计算。
- 在所有步骤的输入参数确认完毕后，最后再确认计算流程的初始输入参数有哪些以及如何定义。
- 每一个计算步骤的输入参数，可能来自于：
  - 计算流程的初始输入，
  - 前置步骤的输出，
  - 该步骤自己设置的默认输入。
- 所有参数名称必须使用蛇形命名法（小写字母、数字、下划线，以字母开头）。
- 在inputs中，对于str类型的输入参数，必须在input_desc中严格说明并限制所有可取的、标准的字符串值，避免出现其他混乱的字符串
- 只要参数涉及计量单位，必须在参数描述中明确注明单位。

### 特别提醒
- 最后请全部以英文输出结果，禁止出现任何中文字符！！
"""

# 依赖验证阶段的提示词
# 需要的输入包含【上下文字典】和【当前步骤】
DEPENDENCY_VERIFICATION_PROMPT = """
### 任务说明
- 你是一个计算数据分析专家。你需要在我给出的【上下文字典】context 中，找到【当前步骤】的每个输入参数的值的来源，并输出一个简化的来源映射字典。
- 输出一个字典 `input_source_dict`，其结构为：
{
    "输入参数名1": "该参数的来源字符串",
    "输入参数名2": "该参数的来源字符串",
    ...
}

### 来源字符串的格式
- 如果参数来源于上下文中的**初始输入**（inputs），则格式为：`$|inputs|.xxx`，其中 `xxx` 为初始输入参数名。
- 如果参数来源于前面某个**步骤的输出**，则格式为：`$|num|.xxx`，其中 num 为步骤编号（字符串），`xxx` 为该步骤输出的参数名。
- 如果参数**无需输入**，直接绑定一个静态值（即不依赖上下文），则直接输出该静态值的字符串表示，例如 `"male"`、`"42"`、`"true"` 等。

### 约束与检查
- 你必须从给定的 `context` 中查找每个输入参数的来源。`context` 包含 `inputs` 列表（初始输入）和各步骤的输出列表（以步骤编号为 key）。
- 来源引用的 key 必须严格匹配 `context` 中定义的参数名（`input_name` 或 `output_name`），不可自行修改。
- 如果参数来源是静态值，请直接输出该值的字符串形式（无需使用 `$||` 包裹）。
- 输出只包含当前步骤中定义的所有输入参数，不要遗漏。

### 输出格式
# 以 JSON 格式输出，以xml标签对<json></json>封装，禁止使用```json ```的标记来封装
<json>
{
    "param1": "source_or_static_value1",
    "param2": "source_or_static_value2"
}
</json>

### 输出示例

**示例1：全部来源于上下文**
<json>
{
    "gender": "$|inputs|.gender",
    "age_list": "$|1|.age_list",
    "diabetes_history": "$|2|.diabetes_score"
}
</json>

**示例2：部分为静态值**
<json>
{
    "weight_kg": "$|inputs|.weight_kg",
    "height_m": "$|inputs|.height_m",
    "unit_system": "metric",
    "round_decimal": "2"
}
</json>

### 上下文字典示例
{
    "inputs": [
        {"input_name": "gender", "input_desc": "...", "input_type": "string"},
        {"input_name": "weight_kg", "input_desc": "...", "input_type": "float"}
    ],
    "1": [
        {"output_name": "age_list", "output_desc": "...", "output_type": "list"}
    ],
    "2": [
        {"output_name": "diabetes_score", "output_desc": "...", "output_type": "integer"}
    ]
}

### 特别提醒
- 最后请全部以英文输出结果，禁止出现任何中文字符！！
"""


# 代码生成阶段的提示词
# 需要的输入包含【计算流程】
CODE_GENERATION_PROMPT = """
### 任务说明
- 你是一个医学领域的计算代码生成专家，你需要根据我给出【计算流程】定义，生成一段整体的计算代码
- 代码整体包含在一个solve()函数中，该函数的输入参数为明确定义的各个参数（而非一个字典参数），例如：def solve(age, weight, height, ...):
- 代码用Python实现，注释中需要标明各个步骤的代码在哪里开始执行
- 每个步骤结尾的位置，用 yield 语句返回当前步骤的输出，返回的内容必须是一个字典，格式为：
  {
      "step_name": "步骤名称（如：计算BMI）",
      "step_description": "稍微详细地描述这一步做了什么（如：根据体重(kg)和身高(m)计算身体质量指数，返回BMI的值）",
      "step_result": 步骤的计算结果（数值或字符串等），
      "unit": "结果对应的单位。有单位的物理量运算结果都应该设置单位，如BMI->kg/m²，纯分数则设为score"
  }
- 代码需要包含必要的注释，说明每个步骤的执行逻辑
- 最终输出项用 return 语句返回

### 输出格式
<python>
import ... # 如果需要引入其他标准库，需要在开头显式声明

def solve(param1, param2, ...):  # 参数必须逐个明确定义，不可使用字典作为唯一参数
    # 代码实现
    # 每个步骤结尾：yield {"step_name": ..., "step_description": ..., "step_result": ..., "unit": ...}
    return final_result  # 最终输出项用 return 语句返回...
</python>

### 重要提示
- import 标准库时，必须为 import <模块名> 的形式，在函数代码中用 <模块名>.<方法名>的形式调用，禁止 from <模块名> import <方法名> 的形式 （例如使用 import datetime，不使用 from datetime import datetime, timedelta）
- solve() 函数的所有输入参数，必须与【计算流程】中 inputs 中的参数个数和名称一致。
- 严格按照【输出格式】进行输出，禁止输出多余内容。以标签对<python></python>封装，禁止使用```python ```的标记来封装
- yield 的字典必须包含 step_name、step_description、step_result、unit 四个键，键的顺序按上述为准，step_description 紧跟在 step_name 后面。
- 必须 return 最终计算结果，不可为None

### 特别提醒
- 检查solve() 函数的输入参数，禁止随意增加 【计算流程】inputs 中未声明的参数！！
- 最后请全部以英文输出结果，禁止出现任何中文字符！！
"""


# 参数抽取提示词
EXTRACT_PARAMETERS_PROMPT = """
### 任务说明
你是一个医疗文本信息的参数抽取专家，请你根据我给出的【参数定义】从【病人信息】中抽取所需的所有参数。
- 我会为你提供【病人信息】和【参数定义】，请严格按照【参数定义】中的参数名称input_name和类型input_type进行抽取。
- input_desc字段如果严格限制了可取的标准值，则你给出的抽取结果必须从中选择，禁止自己创造其他非标准的值
- 如果某个参数需要具体数字作为值，但在【病人信息】中没有找到，标记为 None。

### 输出格式
# 以 JSON 格式输出，以xml标签对<json></json>封装，禁止使用```json ```的标记来封装
<json>
{
    "参数名1": "参数值1",
    "参数名2": "参数值2",
    ...
}
</json>

### 输出示例
<json>
{
    "age": "45",
    "gender": "male",
    "height": "170",
    "weight": "70",
    "diabetes": "yes",
    "smoking": "no",
}
</json>

### 特别提醒
- 最终输出结果全部为英文，禁止出现中文字符！！
- 数值类型的参数，禁止用字符串类型表示，直接用数字类型表示（int 或 float）
"""

# 参数抽取提示词（结构化版，输出遵循 ExtractedParam 模型）
EXTRACT_PARAMETERS_STRUCTURED_PROMPT = """
### 任务说明
你是一个医疗文本信息的参数抽取专家，请你根据我给出的【参数定义】从【病人信息】中抽取所需的所有参数。
- 我会为你提供【病人信息】和【参数定义】，请严格按照【参数定义】中的参数名称 input_name 和类型 input_type 进行抽取。
- input_desc 字段如果严格限制了可取的标准值，则你给出的抽取结果必须从中选择，禁止自己创造其他非标准的值
- 如果某个参数需要具体数字作为值，但在【病人信息】中没有找到，标记为 null，不要编造。

### 输出格式
以 JSON 数组格式输出，每个元素为一个参数抽取结果对象，以 xml 标签对 `<json></json>` 封装，禁止使用 ```json ``` 的标记来封装。

每个参数对象包含以下字段：
- **name** (string): 参数名称，对应【参数定义】中的 input_name
- **rawValue** (string): 从【病人信息】原文中截取的原始文本片段，即病人信息中直接描述该参数的原句或短语
- **normalizedValue** (string | number): 标准化后的参数值。如果是数值类型（int/float），直接输出数字；如果是枚举/分类类型，输出标准值字符串。如果未找到则输出 null
- **unit** (string): 参数的单位。如果【参数定义】中指定了单位则使用该单位；如果原文中带有单位则提取原文单位；如果参数无单位（如性别、是否吸烟等分类值），输出空字符串 ""
- **confidence** (integer): 抽取置信度，取值范围 0~5：
  - 5: 原文明确提及，且值与参数定义完全匹配
  - 4: 原文明确提及，可以通过简单推理确定
  - 3: 原文间接提及，需要一定推理
  - 2: 原文模糊提及，存在一定不确定性
  - 1: 原文仅有一丝线索，高度不确定
  - 0: 未找到，完全无法抽取

### 输出格式模板
<json>
[
    {
        "name": "参数名1",
        "rawValue": "原文中描述该参数的原始文本片段",
        "normalizedValue": "标准化值或数字",
        "unit": "单位或空字符串",
        "confidence": 5
    },
    {
        "name": "参数名2",
        "rawValue": "原文中的原始文本片段",
        "normalizedValue": 70,
        "unit": "kg",
        "confidence": 4
    }
]
</json>

### 输出示例
假设【病人信息】为："Patient is a 45-year-old male, height 170cm, weight 70kg, with history of type 2 diabetes, non-smoker."
【参数定义】中包含 age, gender, height, weight, diabetes, smoking 等参数。

<json>
[
    {
        "name": "age",
        "rawValue": "45-year-old",
        "normalizedValue": 45,
        "unit": "years",
        "confidence": 5,
        "position": { "start": 14, "end": 26 }
    },
    {
        "name": "gender",
        "rawValue": "male",
        "normalizedValue": "male",
        "unit": "",
        "confidence": 5,
        "position": { "start": 27, "end": 31 }
    },
    {
        "name": "height",
        "rawValue": "height 170cm",
        "normalizedValue": 170,
        "unit": "cm",
        "confidence": 5,
        "position": { "start": 33, "end": 46 }
    },
    {
        "name": "weight",
        "rawValue": "weight 70kg",
        "normalizedValue": 70,
        "unit": "kg",
        "confidence": 5,
        "position": { "start": 48, "end": 59 }
    },
    {
        "name": "diabetes",
        "rawValue": "history of type 2 diabetes",
        "normalizedValue": "yes",
        "unit": "",
        "confidence": 5,
        "position": { "start": 61, "end": 88 }
    },
    {
        "name": "smoking",
        "rawValue": "non-smoker",
        "normalizedValue": "no",
        "unit": "",
        "confidence": 5,
        "position": { "start": 90, "end": 100 }
    }
]
</json>

### 特别提醒
- 最终输出结果全部为英文，禁止出现中文字符！！
- normalizedValue 中数值类型的参数，禁止用字符串类型表示，直接用数字类型表示（int 或 float）
- position 中的 start 和 end 必须是精确的字符索引，对应 rawValue 在【病人信息】原文中的起止位置
- 如果【参数定义】中指定的某个参数在【病人信息】中完全找不到，仍需在数组中包含该参数，rawValue 为空字符串 ""，normalizedValue 为 null，confidence 为 0，position 为 { "start": -1, "end": -1 }
- 不要遗漏【参数定义】中的任何参数，每个参数都必须出现在输出数组中

### 格式提醒
- 严格参照输出格式模板，用XML标签对<json></json>封装json结果
- 末尾的</json>标签不能遗漏
"""