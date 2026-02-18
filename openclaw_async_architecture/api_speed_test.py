#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API速度测试脚本
测试所有已配置的API响应速度
"""

import time
import requests
import statistics
from datetime import datetime
import json
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
        "model": "z-ai/glm4.7",
        "note": "思考模式 enabled"
    },
    "英伟达2 (备用)": {
        "provider": "nvidia",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "api_key": "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",
        "model": "z-ai/glm4.7",
        "note": "思考模式 enabled"
    },
    "混元 (腾讯)": {
        "provider": "hunyuan",
        "url": "https://api.hunyuan.cloud.tencent.com/v1/chat/completions",
        "api_key": "sk-7xGaNZwkW0CLZNeT8kZrJv2hiHpU47wzS8XVhOagKKjLyb2i",
        "model": "hunyuan-lite",
        "note": "256k上下文，无RPM限制"
    },
    "SiliconFlow (embeddings)": {
        "provider": "siliconflow",
        "url": "https://api.siliconflow.cn/v1/embeddings",
        "api_key": "sk-kvqpfofevcxloxexrrjovsjzpnwsvhpwrbxkwjydwbjyufjf",
        "model": "BAAI/bge-large-zh-v1.5",
        "note": "仅用于embeddings"
    }
}

# 测试提示词
TEST_PROMPT_SIMPLE = "你好"
TEST_PROMPT_COMPLEX = "请写一个100字的关于人工智能发展的小故事"
TEST_PROMPT_EMBEDDING = "人工智能发展的重要意义"


class APITester:
    def __init__(self):
        self.results = {}

    def test_chat_completion(self, name, config, prompt, test_rounds=3):
        """测试聊天API"""
        print(f"\n{'='*70}")
        print(f"测试: {name}")
        print(f"配置: {config}")
        print(f"提示词: {prompt}")
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

        latencies = []
        responses = []
        tokens = []

        for i in range(test_rounds):
            print(f"\n第 {i+1}/{test_rounds} 轮测试...")

            try:
                start_time = time.time()

                response = requests.post(
                    config['url'],
                    headers=headers,
                    json=payload,
                    timeout=120
                )

                end_time = time.time()
                latency = end_time - start_time

                response.raise_for_status()
                result = response.json()

                # 提取信息
                try:
                    content = result['choices'][0]['message']['content']
                except (KeyError, IndexError, TypeError) as e:
                    print(f"  ✗ 解析响应失败: {e}")
                    print(f"  ✗ 响应结构: {result}")
                    return None

                total_tokens = result.get('usage', {}).get('total_tokens', 0)

                # 检查content是否为None或空
                if content is None or content == "":
                    print(f"  ✗ 响应内容为空")
                    return None

                latencies.append(latency)
                responses.append(content)
                tokens.append(total_tokens)

                print(f"  ✓ 延迟: {latency:.2f}秒")
                print(f"  ✓ Tokens: {total_tokens}")
                print(f"  ✓ 响应长度: {len(content)}字符")

                # 显示响应（截断）
                short_content = content[:100] + "..." if len(content) > 100 else content
                print(f"  ✓ 响应: {short_content}")

            except requests.exceptions.RequestException as e:
                print(f"  ✗ 错误: {e}")
                return None

        # 统计
        stats = {
            "avg_latency": statistics.mean(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "avg_tokens": statistics.mean(tokens),
            "responses": responses,
            "all_latencies": latencies,
            "all_tokens": tokens
        }

        print(f"\n📊 统计结果:")
        print(f"  平均延迟: {stats['avg_latency']:.2f}秒")
        print(f"  最小延迟: {stats['min_latency']:.2f}秒")
        print(f"  最大延迟: {stats['max_latency']:.2f}秒")
        print(f"  平均Tokens: {stats['avg_tokens']:.0f}")

        return stats

    def test_embeddings(self, name, config, prompt, test_rounds=3):
        """测试Embedding API"""
        print(f"\n{'='*70}")
        print(f"测试: {name} (Embeddings)")
        print(f"配置: {config}")
        print(f"提示词: {prompt}")
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

        latencies = []
        dimensions = []

        for i in range(test_rounds):
            print(f"\n第 {i+1}/{test_rounds} 轮测试...")

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

                dims = len(result['data'][0]['embedding'])

                latencies.append(latency)
                dimensions.append(dims)

                print(f"  ✓ 延迟: {latency:.2f}秒")
                print(f"  ✓ 维度: {dims}")

            except requests.exceptions.RequestException as e:
                print(f"  ✗ 错误: {e}")
                return None

        # 统计
        stats = {
            "avg_latency": statistics.mean(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "dimensions": dimensions[0] if dimensions else 0,
            "all_latencies": latencies
        }

        print(f"\n📊 统计结果:")
        print(f"  平均延迟: {stats['avg_latency']:.2f}秒")
        print(f"  最小延迟: {stats['min_latency']:.2f}秒")
        print(f"  最大延迟: {stats['max_latency']:.2f}秒")
        print(f"  向量维度: {stats['dimensions']}")

        return stats

    def run_all_tests(self):
        """运行所有测试"""
        print(f"\n{'='*70}")
        print(f"API速度测试开始")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")

        # 测试简单提示词
        print(f"\n\n{'#'*70}")
        print(f"# 测试1: 简单提示词")
        print(f"{'#'*70}\n")

        for name, config in API_CONFIGS.items():
            if config['provider'] != 'siliconflow':
                result = self.test_chat_completion(
                    name, config, TEST_PROMPT_SIMPLE, test_rounds=3
                )
                if result:
                    self.results[f"{name}_simple"] = result

        # 测试复杂提示词
        print(f"\n\n{'#'*70}")
        print(f"# 测试2: 复杂提示词")
        print(f"{'#'*70}\n")

        for name, config in API_CONFIGS.items():
            if config['provider'] != 'siliconflow':
                result = self.test_chat_completion(
                    name, config, TEST_PROMPT_COMPLEX, test_rounds=3
                )
                if result:
                    self.results[f"{name}_complex"] = result

        # 测试Embeddings
        print(f"\n\n{'#'*70}")
        print(f"# 测试3: Embeddings")
        print(f"{'#'*70}\n")

        for name, config in API_CONFIGS.items():
            if config['provider'] == 'siliconflow':
                result = self.test_embeddings(
                    name, config, TEST_PROMPT_EMBEDDING, test_rounds=3
                )
                if result:
                    self.results[f"{name}_embeddings"] = result

        # 生成汇总报告
        self.generate_report()

    def generate_report(self):
        """生成汇总报告"""
        print(f"\n\n{'#'*70}")
        print(f"# 📊 API速度测试汇总报告")
        print(f"{'#'*70}\n")

        # 简单提示词对比
        print(f"{'='*70}")
        print(f"测试1: 简单提示词 ('你好')")
        print(f"{'='*70}\n")
        self.print_comparison_table("simple")

        # 复杂提示词对比
        print(f"\n\n{'='*70}")
        print(f"测试2: 复杂提示词 (100字故事)")
        print(f"{'='*70}\n")
        self.print_comparison_table("complex")

        # Embeddings测试
        print(f"\n\n{'='*70}")
        print(f"测试3: Embeddings")
        print(f"{'='*70}\n")

        embeddings_key = "SiliconFlow (embeddings)_embeddings"
        if embeddings_key in self.results:
            result = self.results[embeddings_key]
            print(f"提供商: SiliconFlow")
            print(f"模型: BAAI/bge-large-zh-v1.5")
            print(f"平均延迟: {result['avg_latency']:.2f}秒")
            print(f"最小延迟: {result['min_latency']:.2f}秒")
            print(f"最大延迟: {result['max_latency']:.2f}秒")
            print(f"向量维度: {result['dimensions']}")

        # 总体排名
        print(f"\n\n{'#'*70}")
        print(f"# 🏆 速度排名")
        print(f"{'#'*70}\n")

        self.print_ranking("simple", "简单提示词")
        self.print_ranking("complex", "复杂提示词")

        # 保存JSON报告
        self.save_json_report()

    def print_comparison_table(self, test_type):
        """打印对比表格"""
        print(f"{'提供商':<20} {'模型':<15} {'平均延迟(秒)':<12} {'最小延迟(秒)':<12} {'最大延迟(秒)':<12}")
        print(f"{'-'*70}")

        for key, result in self.results.items():
            if key.endswith(f"_{test_type}"):
                name = key.replace(f"_{test_type}", "")
                model = "z-ai/glm4.7" if "英伟达" in name else "hunyuan-lite"
                print(f"{name:<20} {model:<15} "
                      f"{result['avg_latency']:<12.2f} "
                      f"{result['min_latency']:<12.2f} "
                      f"{result['max_latency']:<12.2f}")

    def print_ranking(self, test_type, label):
        """打印排名"""
        print(f"\n{label}排名:")
        print(f"{'排名':<6} {'提供商':<20} {'平均延迟(秒)':<12} {'备注':<30}")
        print(f"{'-'*68}")

        # 提取结果并排序
        items = [(key, result) for key, result in self.results.items()
                 if key.endswith(f"_{test_type}")]
        items.sort(key=lambda x: x[1]['avg_latency'])

        for rank, (key, result) in enumerate(items, 1):
            name = key.replace(f"_{test_type}", "")
            note = ""
            if "英伟达1" in name:
                note = "思考模式"
            elif "英伟达2" in name:
                note = "思考模式"
            elif "混元" in name:
                note = "最快"

            medal = ""
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"

            print(f"{rank:<6} {medal} {name:<20} {result['avg_latency']:<12.2f} {note:<30}")

    def save_json_report(self):
        """保存JSON格式报告"""
        report = {
            "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "api_configs": API_CONFIGS,
            "test_results": self.results
        }

        filename = f"api_speed_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n\n✅ JSON报告已保存: {filename}")


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
