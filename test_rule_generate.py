import asyncio
import json

from services import metric_store


# ── 测试数据 ──

question = "计算患者BMI值"
formula = "BMI=体重(kg)/身高(m)^2"


async def main():
    print("=" * 60)
    print("【create_metric 测试】")
    print(f"question: {question}")
    print(f"formula: {formula}")
    print("=" * 60)

    metric_store.load_metrics()
    print(f"测试前指标数量: {len(metric_store._metrics)}")

    result = await metric_store.create_metric(question, formula)

    print(f"\n【创建结果】")
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
    print(f"\n内存指标数量: {len(metric_store._metrics)}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
