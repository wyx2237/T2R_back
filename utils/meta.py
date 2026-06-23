"""指标元信息管理 —— 为新指标生成 department/code/reference/id，维护 meta.json"""

import json
import os
import re
import uuid
from collections import Counter

# ── LLM Prompt ──

METRIC_INFO_PROMPT = """
### 任务说明
你是一个医学临床指标管理专家，请根据我提供的【指标问题】和【计算公式】，判断该指标所属的科室（department）和参考依据（reference）。

要求：
1. **name**: 确定指标的规范名称，英文全称 + 简写 (如 Body Mass Index (BMI)) ，如果全称很长（远远超过6个单词，则只用简称即可）
2. **department**: 确定指标所属的临床科室/领域（如 Cardiology、Nephrology、Endocrinology、Pulmonology、Gastroenterology、Neurology、Hematology、Oncology、InfectiousDisease、General 等）。如果指标是通用基础指标（如 BMI），使用 "General"
3. **reference**: 给出该指标计算方法的依据来源（如临床指南、权威论文、标准公式名称等），控制在 100 字符以内

### 输出格式
以 ```json ``` 标记封装，输出如下 JSON 对象：

```json
{{
    "name": "<指标名称>"
    "department": "<科室名称>",
    "reference": "<参考依据>"
}}
```

### 输入内容
#【指标问题】
{question}
#【计算公式/描述】
{formula}
"""

# ── 科室简写生成 ──

def _generate_dept_code(name: str, existing_codes: set) -> str:
    """
    为科室名称生成唯一的 3 位大写字母简写，采用多策略降级，保证不重复。

    Args:
        name: 科室名称（如 "Nephrology"）
        existing_codes: 已被占用的 code_name 集合

    Returns:
        3 位大写字母简写（如 "NEP"）
    """
    clean_name = re.sub(r'[^a-zA-Z]', '', name)
    if not clean_name:
        clean_name = "UNKNOWN"
    clean_name = clean_name.upper()

    def candidates():
        # 策略1: 取前三个字母
        if len(clean_name) >= 3:
            yield clean_name[:3]

        # 策略2: 首字母 + 第二字母 + 末尾字母
        if len(clean_name) >= 3:
            yield clean_name[0] + clean_name[1] + clean_name[-1]

        # 策略3: 首字母 + 首个非元音字母 + 末尾字母
        vowels = set('AEIOU')
        for ch in clean_name[1:]:
            if ch not in vowels:
                second_char = ch
                break
        else:
            second_char = clean_name[1] if len(clean_name) > 1 else 'X'
        last_char = clean_name[-1] if len(clean_name) >= 3 else 'X'
        yield clean_name[0] + second_char + last_char

        # 策略4: 多词取首字母（最多3个）
        words = re.findall(r'[A-Za-z]+', name)
        if len(words) >= 2:
            first_letters = [w[0].upper() for w in words[:3]]
            code = ''.join(first_letters).ljust(3, 'X')[:3]
            yield code

        # 策略5: 前 2 字母 + 数字后缀
        if len(clean_name) >= 2:
            prefix = clean_name[:2]
            for digit in range(10):
                yield prefix + str(digit)
        else:
            for digit in range(10):
                yield "D" + str(digit).rjust(2, '0')

    for code in candidates():
        if code not in existing_codes:
            existing_codes.add(code)
            return code

    # 极端保底：前两字母 + 两位数字（取3位）
    base = clean_name[:2] if len(clean_name) >= 2 else "XX"
    for i in range(100):
        candidate = (base + str(i))[:3]
        if candidate not in existing_codes:
            existing_codes.add(candidate)
            return candidate
    return "ERR"


# ── meta.json 读写 ──

META_PATH = "data/meta.json"
METRICS_PATH = "data/metrics.json"


def _load_meta() -> dict:
    """加载 meta.json，不存在则返回空结构"""
    if not os.path.exists(META_PATH):
        return {"metrics": {"department": []}}
    with open(META_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_metrics() -> list:
    """加载 metrics.json，不存在则返回空列表"""
    if not os.path.exists(METRICS_PATH):
        return []
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_meta(meta_data: dict) -> None:
    """写回 meta.json"""
    os.makedirs(os.path.dirname(META_PATH), exist_ok=True)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=2)


# ── 元信息生成 ──

async def metric_info_generate(question: str, formula: str) -> dict:
    """
    为新指标生成元信息：id、name、code、department、reference。

    1. 通过 LLM 判断 department 和 reference
    2. 与已有 meta.json 中的科室匹配 → 复用或新建 code_name
    3. code = code_name + 3 位自增编号
    4. id = uuid

    Args:
        question: 指标计算问题（如 "计算患者BMI值"）
        formula: 计算公式或描述（如 "BMI=体重/身高^2"）

    Returns:
        {"id": str, "code": str, "department": str, "reference": str}
    """
    from services.core.Models import chat_method
    from utils.regex_tools import regex_json_doc

    # 1. 加载现有科室信息
    meta = _load_meta()
    existing_depts = meta.get("metrics", {}).get("department", [])
    dept_map = {d["name"]: d["code_name"] for d in existing_depts}  # name → code_name

    # 2. 构建已有科室名列表（供 prompt 参考）
    dept_names = list(dept_map.keys())

    # 3. 调用 LLM 获取 name、department 和 reference
    prompt = METRIC_INFO_PROMPT.format(
        question=question,
        formula=formula,
        existing_departments="\n".join(f"- {d}" for d in dept_names) if dept_names else "（无已有科室）",
    )

    try_times = 0
    MAX_RETRY = 3
    while try_times < MAX_RETRY:
        try:
            answer = await chat_method(prompt)
            json_str = regex_json_doc(answer)
            info = json.loads(json_str)
            department = info.get("department", "General")
            reference = info.get("reference", "")
            rule_name = info.get("name", "")
            break
        except Exception as e:
            try_times += 1
            print(f"【metric_info_generate error】: {e}")
            print(f"【metric_info_generate retry】: {try_times}/{MAX_RETRY}")
    else:
        # 重试耗尽，使用默认值
        department = "General"
        reference = ""

    # 4. 匹配科室：精确匹配优先
    if department in dept_map:
        code_name = dept_map[department]
    else:
        # 生成新简写
        used_codes = set(dept_map.values())
        code_name = _generate_dept_code(department, used_codes)

    # 5. 计算 code 编号：同前缀已有最大 + 1
    metrics = _load_metrics()
    max_num = 0
    prefix = f"{code_name}-"
    for m in metrics:
        existing_code = m.get("code", "")
        if existing_code.startswith(prefix):
            try:
                num = int(existing_code[len(prefix):])
                max_num = max(max_num, num)
            except ValueError:
                pass
    next_num = max_num + 1
    code = f"{code_name}-{next_num:03d}"

    # 6. 生成唯一 id
    metric_id = uuid.uuid4().hex[:12]

    return {
        "id": metric_id,
        "code": code,
        "name": rule_name,
        "department": department,
        "reference": reference,
    }


# ── meta.json 生成/更新 ──

def generate_meta(metric_data: list) -> dict:
    """
    根据 metrics 列表更新 meta.json 统计信息。
    - 已有科室：保留原有 code_name
    - 新增科室：自动生成唯一简写

    Args:
        metric_data: Metric 对象列表 或 字典列表，需包含 department 字段

    Returns:
        dict: meta.json 结构 {"metrics": {"department": [...], "total_nums": ...}}
    """
    # 1. 加载已有 meta，提取 department → code_name 映射
    existing_meta = _load_meta()
    existing_depts = existing_meta.get("metrics", {}).get("department", [])
    preserved_codes = {d["name"]: d["code_name"] for d in existing_depts}

    # 2. 统计当前各科室指标数
    dept_counter = Counter()
    for m in metric_data:
        dept = m.get("department") if isinstance(m, dict) else getattr(m, "department", None)
        if not dept:
            dept = "Unknown"
        dept_counter[dept] += 1

    # 3. 为每个科室分配或保留 code_name
    sorted_depts = sorted(dept_counter.keys())
    assigned_codes = set()
    department_list = []

    for dept in sorted_depts:
        if dept in preserved_codes:
            # 已有科室：保留原有简写
            code_name = preserved_codes[dept]
            assigned_codes.add(code_name)
        else:
            # 新科室：生成新简写
            code_name = _generate_dept_code(dept, assigned_codes)
            assigned_codes.add(code_name)

        department_list.append({
            "name": dept,
            "code_name": code_name,
            "nums": dept_counter[dept],
        })

    meta_data = {
        "metrics": {
            "department": department_list,
            "total_nums": len(metric_data),
        }
    }

    # 4. 写回文件
    _save_meta(meta_data)
    return meta_data
