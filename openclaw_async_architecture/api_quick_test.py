#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API快速测试脚本 - 单次测试，快速得出结果
"""

import time
import requests
from datetime import datetime
import sys
import io

# 修复Windows GBK编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# API配置清单
API_CONFIGS = {
    "英伟达1 (主账户)": {
        "provider": "nvidia",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "api_key": "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",
        "model": "z-ai/glm4.7"
    },
    "英伟达2 (备用)": {
        "provider": "nvidia",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "api_key": "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",
        "model": "z-ai/glm4.7"
    },
    "混元 (腾讯)": {
        "provider": "hunyuan",
        "url": "https://api.hunyuan.cloud.tencent.com/v1/chat/completions",
        "api_key": "sk-7xGaNZwkW0CLZNeT8kZrJv2hiHpU47wzS8XVhOagKKjLyb2i",
        "model": "hunyuan-lite"
    },
    "SiliconFlow (embeddings)": {
        "provider": "siliconflow",
        "url": "https://api.siliconflow.cn/v1/embeddings",
        "api_key": "sk-kvqpfofevcxloxexrrjovsjzpnwsvhpwrbxkwjydwbjyufjf",
        "model": "BAAI/bge-large-zh-v1.5"
    }
}

def test_chat_api(name, config, prompt):
    """测试聊天API（单次）"""
    print(f"\n{'='*70}")
    print(f"测试: {name}")
    print(f"{'='*70}")

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": config['model'],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 1000
    }

    # 英伟达特有参数
    if config['provider'] == 'nvidia':
        payload['extra_body'] = {
            "chat_template_kwargs": {
                "enable_thinking": True,
                "clear_thinking": False
            }
        }

    try:
        start_time = time.time()

        response = requests.post(
            config['url'],
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
        except (KeyError, IndexError, TypeError):
            print(f"  ✗ 解析响应失败")
            return None

        if content is None or content == "":
            print(f"  ✗ 响应内容为空")
            return None

        total_tokens = result.get('usage', {}).get('total_tokens', 0)

        print(f"  [OK] 延迟: {latency:.2f}秒")
        print(f"  [OK] Tokens: {total_tokens}")
        print(f"  [OK] 响应长度: {len(content)}字符")
        print(f"  [OK] 响应: {content[:100]}{'...' if len(content) > 100 else ''}")

        return {
            "name": name,
            "provider": config['provider'],
            "model": config['model'],
            "latency": latency,
            "tokens": total_tokens,
            "response_length": len(content),
            "response": content
        }

    except requests.exceptions.Timeout:
        print(f"  ✗ 超时 (>60秒)")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  ✗ 错误: {e}")
        return None

def test_embedding_api(name, config, prompt):
    """测试Embedding API（单次）"""
    print(f"\n{'='*70}")
    print(f"测试: {name} (Embeddings)")
    print(f"{'='*70}")

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": config['model'],
        "input": prompt,
        "encoding_format": "float"
    }

    try:
        start_time = time.time()

        response = requests.post(
            config['url'],
            headers=headers,
            json=payload,
            timeout=30
        )

        end_time = time.time()
        latency = end_time - start_time

        response.raise_for_status()
        result = response.json()

        dims = len(result['data'][0]['embedding'])

        print(f"  [OK] 延迟: {latency:.2f}秒")
        print(f"  [OK] 维度: {dims}")

        return {
            "name": name,
            "provider": config['provider'],
            "model": config['model'],
            "latency": latency,
            "dimensions": dims
        }

    except requests.exceptions.RequestException as e:
        print(f"  ✗ 错误: {e}")
        return None

def main():
    """主函数"""
    print(f"\n{'='*70}")
    print(f"API速度测试（快速版 - 单次测试）")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    # 测试简单提示词
    print(f"\n\n{'#'*70}")
    print(f"# 测试1: 简单提示词 ('你好')")
    print(f"{'#'*70}\n")

    results_simple = []
    for name, config in API_CONFIGS.items():
        if config['provider'] != 'siliconflow':
            result = test_chat_api(name, config, "你好")
            if result:
                results_simple.append(result)

    # 测试复杂提示词
    print(f"\n\n{'#'*70}")
    print(f"# 测试2: 复杂提示词 (短故事)")
    print(f"{'#'*70}\n")

    results_complex = []
    for name, config in API_CONFIGS.items():
        if config['provider'] != 'siliconflow':
            result = test_chat_api(name, config, "用50字写一个关于AI的小故事")
            if result:
                results_complex.append(result)

    # 测试Embeddings
    print(f"\n\n{'#'*70}")
    print(f"# 测试3: Embeddings")
    print(f"{'#'*70}\n")

    results_embeddings = []
    for name, config in API_CONFIGS.items():
        if config['provider'] == 'siliconflow':
            result = test_embedding_api(name, config, "AI发展")
            if result:
                results_embeddings.append(result)

    # 生成汇总报告
    print(f"\n\n{'='*70}")
    print(f"📊 API速度测试汇总报告")
    print(f"{'='*70}\n")

    # 简单提示词
    print(f"\n测试1: 简单提示词 ('你好')")
    print(f"{'-'*70}")
    print(f"{'排名':<6} {'提供商':<20} {'延迟(秒)':<12} {'Tokens':<10} {'状态':<10}")
    print(f"{'-'*70}")

    sorted_simple = sorted(results_simple, key=lambda x: x['latency'])
    for rank, result in enumerate(sorted_simple, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        print(f"{rank:<6} {medal} {result['name']:<20} {result['latency']:<12.2f} {result['tokens']:<10} {'OK':<10}")

    # 复杂提示词
    print(f"\n测试2: 复杂提示词 (短故事)")
    print(f"{'-'*70}")
    print(f"{'排名':<6} {'提供商':<20} {'延迟(秒)':<12} {'Tokens':<10} {'状态':<10}")
    print(f"{'-'*70}")

    sorted_complex = sorted(results_complex, key=lambda x: x['latency'])
    for rank, result in enumerate(sorted_complex, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        print(f"{rank:<6} {medal} {result['name']:<20} {result['latency']:<12.2f} {result['tokens']:<10} {'OK':<10}")

    # Embeddings
    print(f"\n测试3: Embeddings")
    print(f"{'-'*70}")
    if results_embeddings:
        result = results_embeddings[0]
        print(f"{result['name']:<20} {result['latency']:<12.2f} {result['dimensions']:<10} {'OK':<10}")

    # 总体排名
    print(f"\n🏆 速度排名（综合）")
    print(f"{'-'*70}")

    # 计算综合排名
    all_results = []
    for result in results_simple:
        all_results.append({
            'name': result['name'],
            'avg_latency': result['latency']
        })
    for result in results_complex:
        for r in all_results:
            if r['name'] == result['name']:
                r['avg_latency'] = (r['avg_latency'] + result['latency']) / 2
                break
        else:
            all_results.append({
                'name': result['name'],
                'avg_latency': result['latency']
            })

    sorted_all = sorted(all_results, key=lambda x: x['avg_latency'])

    for rank, result in enumerate(sorted_all, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        print(f"{rank}. {medal} {result['name']:<20} 平均延迟: {result['avg_latency']:.2f}秒")

    print(f"\n✅ 测试完成！")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
