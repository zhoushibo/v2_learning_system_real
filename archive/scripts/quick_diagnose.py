# -*- coding: utf-8 -*-
"""
OpenClaw 快速诊断和修复
快速诊断常见问题，提供一键修复方案
"""

import os
import sys
import subprocess
from datetime import datetime


def diagnose_and_fix():
    """诊断和修复"""

    print("="*70)
    print("🔧 OpenClaw 快速诊断和修复")
    print("="*70)
    print()

    issues = []
    fixes = []

    # 检查1：Python环境
    print("[检查1] Python环境")
    try:
        subprocess.check_output(["python", "--version"])
        print("  ✅ Python环境正常")
    except:
        print("  ❌ Python环境错误")
        issues.append("Python环境缺失")
        fixes.append("安装Python: https://www.python.org/downloads/")

    # 检查2：OpenClaw安装
    print("\n[检查2] OpenClaw安装")
    try:
        subprocess.check_output([
            "openclaw", "--version"
        ], stderr=subprocess.STDOUT)
        print("  ✅ OpenClaw已安装")

        # 尝试启动
        try:
            subprocess.run([
                "openclaw", "agent", "status"
            ], capture_output=True, timeout=5)
            print("  ✅ OpenClaw可运行")
        except:
            print("  ⚠️  OpenClaw无法运行")
            issues.append("OpenClaw运行错误")
            fixes.append("重新安装OpenClaw: npm install -g @qingchencloud/openclaw-zh --force")
    except:
        print("  ❌ OpenClaw未安装")
        issues.append("OpenClaw未安装")
        fixes.append("安装OpenClaw: npm install -g @qingchencloud/openclaw-zh")

    # 检查3：工作区损坏
    print("\n[检查3] 工作区状态")
    workspace = r"C:\Users\10952\.openclaw\workspace"
    if os.path.exists(workspace):
        # 检查关键文件
        key_files = ["AGENTS.md", "SOUL.md", "MEMORY.md"]
        missing = [f for f in key_files if not os.path.exists(os.path.join(workspace, f))]

        if missing:
            print(f"  ❌ 缺少关键文件: {', '.join(missing)}")
            issues.append("工作区关键文件缺失")
            fixes.append(f"恢复备份: python one_click_restore.py")
        else:
            print("  ✅ 工作区正常")
    else:
        print("  ❌ 工作区不存在")
        issues.append("工作区丢失")
        fixes.append("恢复备份: python one_click_restore.py")

    # 检查4：V2服务状态
    print("\n[检查4] V2服务状态")
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if response.status_code == 200:
            print("  ✅ V2 Gateway运行中")
        else:
            print("  ❌ V2 Gateway响应错误")
            issues.append("V2 Gateway状态异常")
            fixes.append("重启V2: cd openclaw_async_architecture/mvp && python launcher.py")
    except:
        print("  ⚠️  V2 Gateway未运行")
        issues.append("V2 Gateway未运行")
        fixes.append("启动V2: cd openclaw_async_architecture/mvp && python launcher.py")

    # 检查5：Redis状态
    print("\n[检查5] Redis状态")
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
        r.ping()
        print("  ✅ Redis运行中")
    except:
        print("  ❌ Redis未运行")
        issues.append("Redis未运行")
        fixes.append("启动Redis: redis-server")

    # 检查6：备份可用性
    print("\n[检查6] 备份可用性")
    backup_dir = r"D:\ClawBackups"
    if os.path.exists(backup_dir):
        zip_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
        if zip_files:
            print(f"  ✅ 有 {len(zip_files)} 个备份可用")
        else:
            print("  ⚠️  没有备份文件")
            issues.append("无可用备份")
            fixes.append("创建备份: python backup_by_project.py")
    else:
        print("  ⚠️  备份目录不存在")
        issues.append("备份目录丢失")
        fixes.append("创建备份目录: mkdir D:\\ClawBackups")

    print()
    print("="*70)
    print("诊断结果")
    print("="*70)

    if not issues:
        print("✅ 未发现问题，系统运行正常！")
    else:
        print(f"❌ 发现 {len(issues)} 个问题：")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

        print()
        print("="*70)
        print("修复建议")
        print("="*70)

        for i, fix in enumerate(fixes, 1):
            print(f"  {i}. {fix}")

        print()
        print("="*70)
        print("自动修复选项")
        print("="*70)
        print("  1. 从备份恢复（工作区损坏时）")
        print("  2. 重启V2服务（V2服务问题时）")
        print("  3. 启动Redis（Redis未运行时）")
        print("  4. 查看完整健康报告")
        print("  5. 退出")

        choice = input("\n请选择 (1/2/3/4/5): ").strip()

        if choice == "1":
            print("\n🔄 开始从备份恢复...")
            subprocess.run([sys.executable, "one_click_restore.py"])

        elif choice == "2":
            print("\n🔄 重启V2服务...")
            print("  1. 停止现有进程")
            print("  2. 启动新进程")
            print("\n请手动执行以下命令：")
            print("  cd openclaw_async_architecture\\mvp")
            print("  python launcher.py")

        elif choice == "3":
            print("\n🔄 启动Redis...")
            print("  请手动启动Redis服务：")
            print("  redis-server")

        elif choice == "4":
            print("\n📋 运行完整健康检查...")
            subprocess.run([sys.executable, "system_health_check.py"])

        elif choice == "5":
            print("\n退出")

        else:
            print("❌ 无效选择")


if __name__ == "__main__":
    try:
        diagnose_and_fix()
    except Exception as e:
        print(f"\n❌ 诊断失败: {e}")
        import traceback
        traceback.print_exc()
