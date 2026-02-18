# -*- coding: utf-8 -*-
"""并发批量任务提交（使用多进程）"""
import requests
import time
import concurrent.futures
from typing import List, Tuple

GATEWAY_URL = "http://127.0.0.1:8000"


class ConcurrentBatchSubmitter:
    """并发批量任务提交器"""

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.submitted_tasks = []

    def submit_task(self, task_content: str) -> Tuple[str, str]:
        """
        提交单个任务（可并发）

        Args:
            task_content: 任务内容

        Returns:
            (任务ID, 任务内容)
        """
        try:
            response = requests.post(
                f"{GATEWAY_URL}/tasks",
                json={"content": task_content},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                task_id = data['task_id']
                print(f"✅ 任务提交成功: {task_id}")
                return (task_id, task_content)

        except Exception as e:
            print(f"❌ 提交失败: {e}")

        return (None, task_content)

    def submit_batch_concurrent(self, tasks: List[str]) -> List[Tuple[str, str]]:
        """
        并发批量提交任务

        Args:
            tasks: 任务列表

        Returns:
            [(任务ID, 任务内容), ...] 列表
        """
        print("="*70)
        print("🚀 并发批量任务提交")
        print("="*70)
        print(f"总任务数: {len(tasks)}")
        print(f"并发数: {self.max_workers}")
        print()

        results = []

        start_time = time.time()

        # 使用线程池并发提交
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(self.submit_task, task): task
                for task in tasks
            }

            # 等待所有任务完成
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    if result[0]:
                        results.append(result)
                except Exception as e:
                    print(f"❌ 任务异常: {e}")

        elapsed = time.time() - start_time

        print()
        print("="*70)
        print(f"✅ 并发提交完成: {len(results)}/{len(tasks)} 成功")
        print(f"⏱️  总耗时: {elapsed:.2f}秒")
        print(f"⚡ 平均: {elapsed/len(tasks):.2f}秒/任务")
        print("="*70)

        return results

    def wait_and_show_results(self, task_ids: List[str], task_contents: List[str]):
        """等待并显示结果"""
        print()
        print("="*70)
        print("📊 任务结果（等待完成）")
        print("="*70)
        print()

        completed = 0
        start_time = time.time()

        for task_id, content in zip(task_ids, task_contents):
            print(f"⏳ 等待任务: {content[:30]}...")

            # 轮询等待完成
            waited = 0
            max_wait = 60
            while waited < max_wait:
                try:
                    response = requests.get(
                        f"{GATEWAY_URL}/tasks/{task_id}",
                        timeout=5
                    )

                    if response.status_code == 200:
                        task = response.json()
                        if task['status'] in ['completed', 'failed']:
                            break
                except:
                    pass

                time.sleep(1)
                waited += 1

            # 显示结果
            completed += 1
            print(f"✅ [{completed}/{len(task_ids)}] 完成")

        elapsed = time.time() - start_time

        print()
        print("="*70)
        print(f"✅ 所有任务完成")
        print(f"⏱️  总耗时: {elapsed:.2f}秒")
        print("="*70)


def main():
    """主函数"""
    tasks = [
        "介绍一下你自己",
        "翻译：Hello World",
        "写一个Python函数",
        "总结AI发展",
        "推荐Python书籍"
    ]

    # 创建提交器（5并发）
    submitter = ConcurrentBatchSubmitter(max_workers=5)

    # 并发提交
    results = submitter.submit_batch_concurrent(tasks)

    if not results:
        print("❌ 没有任务提交成功")
        return

    task_ids = [r[0] for r in results]
    task_contents = [r[1] for r in results]

    # 等待并显示结果
    submitter.wait_and_show_results(task_ids, task_contents)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  已取消")
