"""测试多模型策略集成"""
import requests
import time
import json

V2_GATEWAY = "http://127.0.0.1:8000"


def test_multi_model_integration():
    """测试多模型策略完整流程"""
    print("="*70)
    print("OpenClaw V2 多模型策略集成测试")
    print("="*70)

    test_cases = [
        {
            "prompt": "你好，请用一句话介绍你自己",
            "type": "simple",
            "expected_model": "hunyuan or zhipu"
        },
        {
            "prompt": "现在马上翻译这句话",
            "type": "realtime",
            "expected_model": "zhipu (最快)"
        },
        {
            "prompt": "深入分析人工智能对社会的影响",
            "type": "complex",
            "expected_model": "nvidia1 (思考模式)"
        },
        {
            "prompt": "批量翻译这100篇文章",
            "type": "bulk",
            "expected_model": "hunyuan (无RPM限制)"
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"测试 {i}/{len(test_cases)}: {test_case['type']}")
        print(f"{'='*70}")
        print(f"提示词: {test_case['prompt']}")
        print(f"预期模型: {test_case['expected_model']}")

        # 提交任务
        start_time = time.time()

        response = requests.post(
            f"{V2_GATEWAY}/tasks",
            json={"content": test_case['prompt']},
            timeout=5
        )

        submit_time = time.time() - start_time

        if response.status_code != 200:
            print(f"❌ 任务提交失败")
            continue

        task_id = response.json()['task_id']
        print(f"✅ 任务提交成功: {task_id}")
        print(f"⏱️  提交时间: {submit_time*1000:.2f}ms")

        # 等待任务完成
        print(f"\n⏳ 等待任务执行...")
        task_result = None
        for j in range(30):
            time.sleep(1)

            response = requests.get(
                f"{V2_GATEWAY}/tasks/{task_id}",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                if data['status'] == "completed":
                    task_result = data
                    break
                elif data['status'] == "failed":
                    print(f"❌ 任务失败: {data['error']}")
                    break

        if task_result:
            print(f"\n✅ 任务完成！")
            print(f"状态: {task_result['status']}")
            print(f"结果: {task_result['result'][:100]}...")

            # 提取模型信息
            if 'metadata' in task_result and task_result['metadata']:
                model = task_result['metadata'].get('model', 'unknown')
                latency = task_result['metadata'].get('latency', 0)
                print(f"\n📊 执行详情:")
                print(f"  🤖 实际使用模型: {model}")
                print(f"  ⏱️  耗时: {latency:.2f}秒")

                results.append({
                    "test": test_case['type'],
                    "prompt": test_case['prompt'],
                    "model": model,
                    "latency": latency,
                    "expected": test_case['expected_model']
                })
            else:
                print(f"\n⚠️  没有元数据信息")

    # 汇总统计
    print(f"\n{'='*70}")
    print("测试汇总")
    print(f"{'='*70}")

    models_used = set(r['model'] for r in results if r['model'] != 'unknown')
    avg_latency = sum(r['latency'] for r in results) / len(results) if results else 0

    print(f"✅ 成功完成: {len(results)}/{len(test_cases)}")
    print(f"✅ 使用的模型: {', '.join(models_used)}")
    print(f"⏱️  平均延迟: {avg_latency:.2f}秒")
    print(f"\n详细结果:")
    print(f"{'测试类型':<15} {'模型':<20} {'耗时(秒)':<10} {'预期'}")
    print(f"{'-'*70}")
    for r in results:
        print(f"{r['test']:<15} {r['model']:<20} {r['latency']:<10.2f} {r['expected']}")

    return len(results) == len(test_cases)


def test_load_balancer_direct():
    """直接测试LoadBalancer"""
    print(f"\n{'='*70}")
    print("LoadBalancer直接测试")
    print(f"{'='*70}")

    import sys
    import os
    sys.path.insert(0, r'C:\Users\10952\.openclaw\workspace\openclaw_async_architecture\mvp\src')

    from common.load_balancer import get_load_balancer

    balancer = get_load_balancer()

    print(f"\n测试不同类型任务:")

    test_prompts = [
        "快速回答：你好",
        "分析：深度思考一个问题",
        "批量：处理很多任务",
        "现在：立即翻译"
    ]

    for prompt in test_prompts:
        print(f"\n{'--'*35}")
        print(f"提示词: {prompt}")

        result = balancer.call_api(prompt)

        if result['success']:
            print(f"✅ 成功")
            print(f"  模型: {result['model']}")
            print(f"  耗时: {result['latency']:.2f}秒")
            print(f"  内容: {result['content'][:80]}...")
        else:
            print(f"❌ 失败: {result.get('error')}")

    # 统计
    print(f"\n{'--'*35}")
    print(f"统计信息:")
    print(json.dumps(balancer.get_stats(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_mode = input("选择测试模式 (1=完整MVP测试, 2=LoadBalancer直接测试): ").strip()

    if test_mode == "2":
        test_load_balancer_direct()
    else:
        success = test_multi_model_integration()

        print(f"\n{'='*70}")
        if success:
            print("✅ 多模型策略集成测试通过！")
        else:
            print("❌ 部分测试失败")
        print(f"{'='*70}")
