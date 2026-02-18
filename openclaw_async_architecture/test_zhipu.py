#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱 glm4.7-flash 速度测试脚本
"""

import time
import requests
from datetime import datetime
import sys
import io

# 修复Windows GBK编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 智谱配置
ZHIPU_CONFIG = {
    "name": "智谱 glm4.7-flash",
    "provider": "zhipu",
    "url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    "api_key": "c744282c23b74fa9bf7a2be68a8656b7.w4rIakRo0j4tWqpO",
    "model": "glm-4-flash",
    "context_window": 200000,
    "max_concurrent": 1,
    "note": "200K上下文，支持 thinkers 模式"
}

def test_zhipu(prompt):
    """测试智谱 API"""
    print(f"\n{'='*70}")
    print(f"测试: {ZHIPU_CONFIG['name']}")
    print(f"提示词: {prompt}")
    print(f"{'='*70}")

    headers = {
        "Authorization": f"Bearer {ZHIPU_CONFIG['api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": ZHIPU_CONFIG['model'],
        "messages": [{"role": "user", "content": prompt}],
        "thinking": {"type": "enabled"},
        "max_tokens": 1024,
        "temperature": 0.7,
        "stream": False
    }

    try:
        start_time = time.time()

        response = requests.post(
            ZHIPU_CONFIG['url'],
            headers=headers,
            json=payload,
            timeout=60
        )

        end_time = time.time()
        latency = end_time - start_time

        response.raise_for_status()
        result = response.json()

        # 提取信息
        try:
            content = result['choices'][0]['message']['content']
            thinking_content = result['choices'][0]['message'].get('thinking_content', '')

        except (KeyError, IndexError, TypeError):
            print(f"  ✗ 解析响应失败")
            print(f"  响应结构: {result}")
            return None

        if content is None or content == "":
            print(f"  ✗ 响应内容为空")
            return None

        total_tokens = result.get('usage', {}).get('total_tokens', 0)

        print(f"  [OK] 延迟: {latency:.2f}秒")
        print(f"  [OK] Tokens: {total_tokens}")
        print(f"  [OK] 响应长度: {len(content)}字符")

        if thinking_content:
            print(f"  [OK] 思考内容: ({len(thinking_content)}字符)")
            print(f"  思考预览: {thinking_content[:100]}...")

        print(f"  [OK] 响应: {content[:100]}{'...' if len(content) > 100 else ''}")

        return {
            "name": ZHIPU_CONFIG['name'],
            "provider": ZHIPU_CONFIG['provider'],
            "model": ZHIPU_CONFIG['model'],
            "latency": latency,
            "tokens": total_tokens,
            "response_length": len(content),
            "response": content,
            "has_thinking": bool(thinking_content)
        }

    except requests.exceptions.Timeout:
        print(f"  ✗ 超时 (>60秒)")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  ✗ 错误: {e}")
        return None

def main():
    """主函数"""
    print(f"\n{'='*70}")
    print(f"智谱 glm4.7-flash 速度测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    # 测试简单提示词
    print(f"\n\n{'#'*70}")
    print(f"# 测试1: 简单提示词 ('你好')")
    print(f"{'#'*70}\n")

    result1 = test_zhipu("你好")

    # 等待一下（确保不会触发并发限制）
    time.sleep(2)

    # 测试复杂提示词
    print(f"\n\n{'#'*70}")
    print(f"# 测试2: 复杂提示词 (短故事)")
    print(f"{'#'*70}\n")

    result2 = test_zhipu("用50字写一个关于AI的小故事")

    # 汇总
    print(f"\n\n{'='*70}")
    print(f"📊 智谱 glm4.7-flash 测试结果")
    print(f"{'='*70}\n")

    if result1 and result2:
        avg_latency = (result1['latency'] + result2['latency']) / 2

        print(f"测试1 (简单): {result1['latency']:.2f}秒, {result1['tokens']} tokens")
        print(f"测试2 (复杂): {result2['latency']:.2f}秒, {result2['tokens']} tokens")
        print(f"\n{'-'*70}")
        print(f"平均延迟: {avg_latency:.2f}秒")
        print(f"思考模式: {'✓ 已启用' if (result1['has_thinking'] or result2['has_thinking']) else '✗ 未启用'}")
        print(f"{'-'*70}")

        # 与其他模型对比（基于之前测试结果）
        print(f"\n🏆 速度对比（基于之前测试结果）")
        print(f"{'-'*70}")
        print(f"{'排名':<6} {'模型':<25} {'平均延迟(秒)':<15} {'上下文':<10}")
        print(f"{'-'*70}")

        # 排序（更新后的排名）
        all_models = [
            {"name": "混元 (腾讯)", "latency": 1.20, "context": "256k"},
            {"name": "英伟达2", "latency": 2.68, "context": "128k"},
            {"name": "智谱 glm4.7-flash", "latency": avg_latency, "context": "200k"},
            {"name": "英伟达1", "latency": 7.17, "context": "128k"}
        ]

        sorted_models = sorted(all_models, key=lambda x: x['latency'])

        for rank, model in enumerate(sorted_models, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
            marker = " ⭐" if "智谱" in model['name'] else ""
            print(f"{rank:<6} {medal} {model['name']:<25} {model['latency']:<15.2f} {model['context']:<10}{marker}")

    else:
        print("✗ 测试失败")

    print(f"\n✅ 测试完成！")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
