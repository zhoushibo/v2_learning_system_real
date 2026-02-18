# -*- coding: utf-8 -*-
"""批量任务提交脚本"""
import requests
import time
import json
from typing import List

GATEWAY_URL = "http://127.0.0.1:8000"


class BatchTaskSubmitter:
    """批量任务提交器"""

    def __init__(self):
        self.submitted_tasks = []

    def submit_task(self, content: str) -> str:
        """
        提交单个任务

        Args:
            content: 任务内容

        Returns:
            任务ID
        """
        try:
            response = requests.post(
                f"{GATEWAY_URL}/tasks",
                json={"content": content},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                task_id = data['task_id']
                self.submitted_tasks.append(task_id)
                print(f"✅ 任务提交成功: {task_id}")
                print(f"   内容: {content[:50]}...")
                return task_id
            else:
                print(f"❌ 提交失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 错误: {e}")
            return None

    def submit_batch(self, tasks: List[str]) -> List[str]:
        """
        批量提交任务

        Args:
            tasks: 任务列表

        Returns:
            任务ID列表
        """
        print("="*70)
        print("🚀 批量任务提交")
        print("="*70)
        print(f"总任务数: {len(tasks)}")
        print()

        task_ids = []

        for i, task in enumerate(tasks, 1):
            print(f"[{i}/{len(tasks)}] 提交任务...")
            task_id = self.submit_task(task)
            if task_id:
                task_ids.append(task_id)
            print()

        print("="*70)
        print(f"✅ 批量提交完成: {len(task_ids)}/{len(tasks)} 成功")
        print("="*70)

        return task_ids

    def check_task_status(self, task_id: str) -> dict:
        """
        检查任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务信息字典
        """
        try:
            response = requests.get(
                f"{GATEWAY_URL}/tasks/{task_id}",
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return None

    def wait_all_tasks(self, task_ids: List[str], timeout: int = 60):
        """
        等待所有任务完成

        Args:
            task_ids: 任务ID列表
            timeout: 超时时间（秒）
        """
        print()
        print("="*70)
        print("⏳ 等待所有任务完成...")
        print("="*70)

        start_time = time.time()
        completed = set()

        while len(completed) < len(task_ids):
            # 检查超时
            if time.time() - start_time > timeout:
                print(f"\n❌ 超时: {timeout}秒")
                break

            # 检查任务状态
            for task_id in task_ids:
                if task_id in completed:
                    continue

                task = self.check_task_status(task_id)
                if task and task['status'] in ['completed', 'failed']:
                    completed.add(task_id)
                    status_icon = "✅" if task['status'] == 'completed' else "❌"
                    print(f"{status_icon} {task_id}: {task['status']}")

            # 等待1秒
            time.sleep(1)

        print()
        print("="*70)
        print(f"✅ 所有任务完成: {len(completed)}/{len(task_ids)}")
        print("="*70)

    def show_results(self, task_ids: List[str]):
        """
        显示所有任务结果

        Args:
            task_ids: 任务ID列表
        """
        print()
        print("="*70)
        print("📊 任务结果")
        print("="*70)
        print()

        for i, task_id in enumerate(task_ids, 1):
            task = self.check_task_status(task_id)

            if task:
                print(f"任务 {i}: {task_id}")
                print(f"  状态: {task['status']}")

                if task['status'] == 'completed':
                    metadata = task.get('metadata', {})
                    print(f"  模型: {metadata.get('model', '未知')}")
                    print(f"  耗时: {metadata.get('latency', 0):.2f}秒")
                    print(f"  结果:")
                    print(f"    {task.get('result', '')[:200]}...")
                elif task['status'] == 'failed':
                    print(f"  错误: {task.get('error', '未知错误')}")
                else:
                    print(f"  状态: {task['status']}")

            print()


def main():
    """主函数"""
    # 定义任务列表
    tasks = [
        "介绍一下你自己",
        "翻译这句话到英文：你好世界",
        "写一个Python函数计算斐波那契数列",
        "总结一下人工智能的发展",
        "推荐几本Python学习书籍"
    ]

    # 创建提交器
    submitter = BatchTaskSubmitter()

    # 批量提交
    task_ids = submitter.submit_batch(tasks)

    if not task_ids:
        print("❌ 没有任务提交成功")
        return

    # 等待所有任务完成
    submitter.wait_all_tasks(task_ids)

    # 显示结果
    submitter.show_results(task_ids)

    print("✅ 批量任务处理完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  已取消")
