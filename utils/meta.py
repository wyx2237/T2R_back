from collections import Counter
import re

def generate_meta(metric_data):
    """
    根据 metric.json 数据生成 meta.json 统计信息，自动处理科室简写冲突。

    参数:
        metric_data (list): metric.json 解析后的列表，每个元素包含 department 字段。

    返回:
        dict: 包含 department 列表和 total_nums 的字典。
    """
    # 统计每个科室的指标数量
    dept_counter = Counter()
    for metric in metric_data:
        dept = metric.get("department")
        if dept is None or dept == "":
            dept = "Unknown"
        dept_counter[dept] += 1

    # 获取唯一的科室列表（保持和 dept_counter 一致）
    unique_depts = list(dept_counter.keys())

    # 为每个科室生成唯一的 code_name
    def generate_unique_code(name, existing_codes):
        """
        为科室名称生成唯一的 3 位大写字母简写。
        采用多策略降级，保证不重复。
        """
        # 预处理：保留字母，统一大写
        clean_name = re.sub(r'[^a-zA-Z]', '', name)
        if not clean_name:
            clean_name = "UNKNOWN"
        clean_name = clean_name.upper()

        # 候选策略生成器
        def candidates():
            # 策略1: 取前三个字母
            if len(clean_name) >= 3:
                yield clean_name[:3]

            # 策略2: 首字母 + 第二个字母 + 最后一个字母
            if len(clean_name) >= 3:
                yield clean_name[0] + clean_name[1] + clean_name[-1]

            # 策略3: 首字母 + 第一个非元音字母（除首字母外）+ 最后一个字母
            vowels = set('AEIOU')
            for i, ch in enumerate(clean_name[1:], start=1):
                if ch not in vowels:
                    second_char = ch
                    break
            else:
                second_char = clean_name[1] if len(clean_name) > 1 else 'X'
            last_char = clean_name[-1] if len(clean_name) >= 3 else 'X'
            yield clean_name[0] + second_char + last_char

            # 策略4: 针对多词（按空格或原名称）取每个单词首字母（最多3个）
            words = re.findall(r'[A-Za-z]+', name)  # 原名称中的单词
            if len(words) >= 2:
                first_letters = [w[0].upper() for w in words[:3]]
                code = ''.join(first_letters).ljust(3, 'X')[:3]
                yield code

            # 策略5: 使用数字后缀（保留前两位字母 + 数字）
            if len(clean_name) >= 2:
                prefix = clean_name[:2]
                for digit in range(10):
                    yield prefix + str(digit)
            else:
                # 名称过短，使用固定前缀 + 数字
                for digit in range(10):
                    yield "D" + str(digit).rjust(2, '0')

        # 遍历所有候选，找到第一个未使用的
        for code in candidates():
            if code not in existing_codes:
                existing_codes.add(code)
                return code

        # 极端情况：所有候选都被占用（几乎不可能），则生成带两位数字的降级方案（会超过3位，但保证唯一）
        # 这里简单返回一个随机三位组合加后缀
        base = clean_name[:2] if len(clean_name) >= 2 else "XX"
        for i in range(100):
            candidate = (base + str(i))[:3]  # 截断保证3位
            if candidate not in existing_codes:
                existing_codes.add(candidate)
                return candidate
        return "ERR"  # 最终保底

    # 按科室名称排序（可选，保证输出稳定）
    unique_depts.sort()
    assigned_codes = set()
    department_list = []
    for dept in unique_depts:
        code = generate_unique_code(dept, assigned_codes)
        department_list.append({
            "name": dept,
            "code_name": code,
            "nums": dept_counter[dept]
        })

    total_nums = len(metric_data)

    return {
        "department": department_list,
        "total_nums": total_nums
    }