"""V2自动化备份脚本"""

import requests
import time
import json

V2_GATEWAY = "http://127.0.0.1:8000"


def submit_backup_task(project_name="V2_Async_Architecture"):
    """
    提交备份任务到V2
    """
    task_content = f"""
    执行项目备份任务：

    项目：{project_name}

    步骤：
    1. 执行备份命令：
       TOOL:exec_command|{{"command":"python backup_by_project.py --project '{project_name}'"}}

    2. 检查备份结果：
       TOOL:exec_python|{{
         "code":"import os, glob; files = glob.glob('D:/ClawBackups/*.zip'); latest = max(files, key=os.path.getctime); print(f'Latest backup: {{latest}}')"
       }}

    3. 记录备份信息到日志：
       TOOL:write_file|{{
         "path":"logs/backup_log.txt",
         "content":"Backup completed at {{datetime}}"
       }}

    请按顺序执行这些步骤，每步完成后告诉我结果。
    """

    # 提交任务
    response = requests.post(
        f"{V2_GATEWAY}/tasks",
        json={
            "content": task_content.strip(),
            "priority": "high"
        }
    )

    task_id = response.json()["task_id"]
    print(f"✅ 备份任务已提交: {task_id}")

    return task_id


def poll_task_result(task_id, timeout=60):
    """
    轮询任务结果
    """
    print("⏳ 等待备份完成...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(f"{V2_GATEWAY}/tasks/{task_id}")
        task = response.json()

        status = task["status"]

        if status == "completed":
            print("\n✅ 备份完成!")
            print(f"结果: {task.get('result', '无结果')}")
            print(f"元数据: {json.dumps(task.get('metadata', {}), indent=2, ensure_ascii=False)}")

            # 如果有详细结果，解析并显示
            if task.get('result'):
                try:
                    result_json = json.loads(task['result'])
                    print(f"\n详细结果: {result_json}")
                except:
                    pass

            return task

        elif status == "failed":
            print(f"\n❌ 备份失败: {task.get('error', '未知错误')}")
            return task

        time.sleep(2)
        print(f"  当前进度: {status}...")

    print(f"\n⏱️  超时: {timeout}秒内未完成")
    return None


def main():
    """主函数"""
    print("="*60)
    print("V2自动化备份系统")
    print("="*60)

    # 提交备份任务
    task_id = submit_backup_task("V2_Async_Architecture")

    # 等待结果
    task = poll_task_result(task_id, timeout=120)  # 2分钟超时

    if task and task["status"] == "completed":
        print("\n" + "="*60)
        print("🎉 V2自动化备份成功！")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ 备份失败或超时")
        print("="*60)


if __name__ == "__main__":
    main()
