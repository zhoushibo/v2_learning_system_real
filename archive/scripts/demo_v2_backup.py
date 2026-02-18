"""V2自动化备份演示（修复版）"""

import requests
import time
import json

V2_GATEWAY = "http://127.0.0.1:8000"


def demo_v2_backup():
    """演示V2自动化备份"""

    print("="*60)
    print("V2自动化备份演示")
    print("="*60)

    print("\n【步骤1】提交备份任务到V2")
    task_content = 'TOOL:exec_command|{"command":"python backup_by_project.py"}'

    response = requests.post(f"{V2_GATEWAY}/tasks", json={"content": task_content})
    task_id = response.json()["task_id"]

    print(f"✅ 任务ID: {task_id}")
    print(f"✅ 命令: python backup_by_project.py")

    print("\n【步骤2】V2 Worker处理中...")

    for i in range(60):
        time.sleep(1)

        response = requests.get(f"{V2_GATEWAY}/tasks/{task_id}")
        task = response.json()

        status = task["status"]

        if status == "completed":
            print(f"\n✅ 备份完成（用时 {i+1} 秒）")

            # 元数据
            print(f"\n【任务信息】")
            metadata = task.get('metadata', {})
            print(f"  类型: {metadata.get('type', 'N/A')}")
            print(f"  工具: {metadata.get('tool_name', 'N/A')}")
            print(f"  命令: {metadata.get('command', 'N/A')}")

            # 尝试解析结果
            result_str = task.get('result', '')
            print(f"\n【命令输出】")
            print(f"  {result_str[:200]}...")

            # 直接查询最新的备份文件
            import os
            import glob
            backup_dir = 'D:/ClawBackups'
            if os.path.exists(backup_dir):
                backup_files = glob.glob(f'{backup_dir}/*.zip')
                if backup_files:
                    latest = max(backup_files, key=os.path.getctime)
                    print(f"\n【最新备份文件】")
                    print(f"  文件: {latest}")
                    print(f"  大小: {os.path.getsize(latest) / 1024:.2f} KB")

            print("\n【关键发现】")
            print(f"  ✅ V2成功执行了备份命令")
            print(f"  ✅ 通过API触发，无需手动运行")
            print(f"  ✅ 可以集成到定时任务中")
            print(f"  ✅ 可以通过工作流编排")
            print(f"  ✅ 响应时间: {i+1} 秒")

            break

        elif status == "failed":
            print(f"\n❌ 备份失败: {task.get('error', 'Unknown error')}")
            break

    print("\n" + "="*60)
    print("🎉 V2自动化备份演示完成！")
    print("="*60)


if __name__ == "__main__":
    demo_v2_backup()
