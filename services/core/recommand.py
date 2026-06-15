RECOMMAND_PROMPT = """
### 任务说明
你是一个医学临床指标计算的专家，现在请你根据我提供的【病人信息】，从【备选计算指标库】中选取 k 个适配程度最高的指标作为【推荐计算指标】。
具体推荐的原则如下：

1.评分计算方式
依次分析指标库中的每个指标，包含以下2个方面
a. 分析病人信息涉及的症状、疾病是否与当前指标有关联？如果不指向特定疾病的通用类型指标，这一项得满分
b. 分析病人信息中是否包含当前指标的必需参数，重点关注需要具体数值或明确枚举值的参数，不关注类似`有无某症状`之类的可推断、非强依赖原始信息的参数
每个方面评分区分为 3，2，1 三档。评分表示为 a[x] + b[y]，例如a[2]+b[3]

2.选取方式
- b为3分时可直接列为【可推荐】，1分时直接列为【不可推荐】
- b为2分时，根据a得分来判断，a为3分时列为【可推荐】，1分时列为【不可推荐】
- b和a均为2分时，查看当前【可推荐】项目是否达到 k 项，未达到则加入，已满则丢弃

3.多样化推荐
可推荐数量超过k个时，随机从中选取k个作为推荐结果，保证多样化推荐需求

### 输出格式
以 JSON 数组格式输出，用 ```json ``` 标记封装。数组中每个元素为一个推荐指标对象，字段结构如下：

- **indicatorId** (string): 指标唯一标识，对应备选指标库中的 id 字段
- **indicatorName** (string): 指标名称
- **scoreA** (integer): 关联度评分（1~3），指标与病人症状/疾病的关联程度。3=通用指标或高度关联，2=中等关联，1=关联度低
- **scoreB** (integer): 参数完整度评分（1~3），病人信息中是否包含指标的必需参数。3=必需参数齐全，2=部分参数缺失但可推断，1=关键参数严重缺失
- **scoreLabel** (string): 评分标签，格式为 "a[{{scoreA}}]+b[{{scoreB}}]"，例如 "a[2]+b[3]"
- **recommend** (boolean): 是否推荐。true=推荐计算该指标，false=不推荐
- **reasonA** (string): scoreA 的评分依据，简要说明指标与病人信息的关联判断
- **reasonB** (string): scoreB 的评分依据，简要说明病人信息中已有和缺失的参数情况
- **overallReason** (string): 综合推荐理由，总结该指标是否适合当前病人的核心原因

```json
[
    {{
        "indicatorId": "<指标id>",
        "indicatorName": "<指标名称>",
        "scoreA": 3,
        "scoreB": 2,
        "scoreLabel": "a[3]+b[2]",
        "recommend": true,
        "reasonA": "<a评分依据>",
        "reasonB": "<b评分依据>",
        "overallReason": "<综合推荐理由>"
    }}
]
```

返回的数组长度应等于 k，即恰好包含 k 个 recommend 为 true 的指标。

### 输出示例
```json
[
    {{
        "indicatorId": "BMI",
        "indicatorName": "身体质量指数(BMI)",
        "scoreA": 3,
        "scoreB": 3,
        "scoreLabel": "a[3]+b[3]",
        "recommend": true,
        "reasonA": "BMI为通用健康指标，不指向特定疾病，关联度得满分",
        "reasonB": "病人信息中明确提供了身高170cm和体重70kg，完全满足BMI计算所需的两个核心参数",
        "overallReason": "病人信息完整包含计算所需参数，BMI作为基础健康评估指标，强烈推荐计算"
    }},
    {{
        "indicatorId": "BSA",
        "indicatorName": "体表面积(BSA)",
        "scoreA": 3,
        "scoreB": 3,
        "scoreLabel": "a[3]+b[3]",
        "recommend": true,
        "reasonA": "BSA为通用生理指标，广泛应用于药物剂量计算等场景，不限于特定疾病",
        "reasonB": "病人信息中明确提供了身高和体重，满足BSA公式计算需求",
        "overallReason": "身高体重数据齐全，BSA是临床常用的基础指标，推荐计算"
    }}
]
```

### 输入内容
#【推荐指标数量】k = {k}
#【备选计算指标库】
{indicators}
#【病人信息】
{patient_info}
"""

from services.core.Models import chat_method
from utils.regex_tools import regex_json_doc
import json

MAX_RETRY_TIMES = 3

async def recommend(raw_text, available_metrics, k):
    """
    从可选的指标列表中，根据当前的文本信息，匹配推荐 k 个最合适的指标。
    最大重试 MAX_RETRY_TIMES 次。
    """
    prompt = RECOMMAND_PROMPT.format(k=k, indicators=available_metrics, patient_info=raw_text)

    try_times = 0
    while try_times < MAX_RETRY_TIMES:
        try:
            answer = await chat_method(prompt)
            # print(f"[Answer]:\n{answer}")
            result = regex_json_doc(answer)
            # print(f"[Result]:\n{result}")
            result = json.loads(result)
            return result
        except Exception as e:
            try_times += 1
            print(f"【recommend error】: {e}")
            print(f"【recommend retry】: {try_times}/{MAX_RETRY_TIMES}")
    raise Exception(f"【recommend error】: 指标推荐失败，已重试 {MAX_RETRY_TIMES} 次，无法完成推荐。")