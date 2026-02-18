# -*- coding: utf-8 -*-
"""完整备份所有工作区到D盘（包括钉钉系统）"""
import shutil
import os
import zipfile
from datetime import datetime


def backup_all_workspaces():
    """备份所有工作区到D盘"""

    # 源目录（两个workspace）
    workspace1 = r"C:\Users\10952\.openclaw\workspace"
    workspace2 = r"D:\.openclaw\workspace"

    # 备份目录
    backup_dir = r"D:\ClawBackups"
    os.makedirs(backup_dir, exist_ok=True)

    # 生成备份名称
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"FULL_WORKSPACE_BACKUP_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)

    print("="*70)
    print("🔧 开始完整备份所有工作区")
    print("="*70)
    print(f"Workspace 1: {workspace1}")
    print(f"Workspace 2: {workspace2}")
    print(f"备份位置: {backup_path}")
    print()

    # 创建压缩文件
    zip_name = f"{backup_path}.zip"
    exclude = ['__pycache__', '*.pyc', '*.pyd', '*.log', '*.tmp', '*.swp',
               'node_modules', '.git', '*.db', '*.sqlite']

    print("📦 正在压缩... (这可能需要几分钟)")
    print()

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total_files = 0

        # 备份workspace1（当前workspace）
        print(f"\n📁 备份 Workspace 1...")
        if os.path.exists(workspace1):
            prefix1 = "workspace_current"
            for root, dirs, files in os.walk(workspace1):
                dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude)]
                for file in files:
                    if any(ex in file for ex in exclude):
                        continue
                    file_path = os.path.join(root, file)
                    rel_path = os.path.join(prefix1, os.path.relpath(file_path, workspace1))
                    zipf.write(file_path, rel_path)
                    total_files += 1
                    if total_files % 100 == 0:
                        print(f"  Workspace 1: {total_files} 个文件...", end='\r')

        # 备份workspace2（含钉钉系统）
        print(f"\n📁 备份 Workspace 2（含钉钉系统）...")
        if os.path.exists(workspace2):
            prefix2 = "workspace_legacy"
            for root, dirs, files in os.walk(workspace2):
                dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude)]
                for file in files:
                    if any(ex in file for ex in exclude):
                        continue
                    file_path = os.path.join(root, file)
                    rel_path = os.path.join(prefix2, os.path.relpath(file_path, workspace2))
                    zipf.write(file_path, rel_path)
                    total_files += 1
                    if total_files % 100 == 0:
                        print(f"  Total: {total_files} 个文件...", end='\r')

    print()
    print(f"✅ 压缩完成！")
    print(f"   备份文件: {zip_name}")
    print(f"   文件数量: {total_files}")
    print(f"   文件大小: {os.path.getsize(zip_name) / 1024 / 1024:.2f} MB")
    print()

    # 验证备份
    print("🔍 验证备份...")
    test_zip = zipfile.ZipFile(zip_name, 'r')
    bad_files = test_zip.testzip()
    test_zip.close()

    if bad_files:
        print(f"❌ 备份验证失败！损坏的文件: {bad_files}")
        return False
    else:
        print("✅ 备份验证成功！")
        print()

    # 创建备份信息文件
    info_file = f"{backup_path}.txt"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(f"完整工作区备份信息\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"备份文件: {zip_name}\n")
        f.write(f"文件数量: {total_files}\n")
        f.write(f"文件大小: {os.path.getsize(zip_name) / 1024 / 1024:.2f} MB\n")
        f.write(f"\n包含内容:\n")
        f.write(f"  - workspace_current/ (C:\\Users\\10952\\.openclaw\\workspace)\n")
        f.write(f"    * openclaw_async_architecture/ (V2 MVP)\n")
        f.write(f"    * memory/ (记忆系统)\n")
        f.write(f"    * TODO.md, PROJECT_LIST.md (项目管理)\n")
        f.write(f"\n")
        f.write(f"  - workspace_legacy/ (D:\\.openclaw\\workspace)\n")
        f.write(f"    * claw_agent_demo/ (钉钉AI Agent) ⭐\n")
        f.write(f"    * novel_tools/ (小说工具)\n")
        f.write(f"    * pipelines/ (工具流水线)\n")
        f.write(f"    * agents/ (代理系统)\n")
        f.write(f"\n")
        f.write(f"钉钉系统文件清单:\n")
        f.write(f"  - demo/dingtalk.py (钉钉适配器)\n")
        f.write(f"  - demo/crypto_utils.py (加解密工具)\n")
        f.write(f"  - demo/server.py (Flask服务器)\n")
        f.write(f"  - demo/agent.py (Agent核心)\n")
        f.write(f"  - .env (配置文件)\n")
        f.write(f"  钉钉Demo文件总数: 17\n")

    print(f"📝 备份信息已保存: {info_file}")
    print()
    print("="*70)
    print("✅ 完整备份成功！")
    print("="*70)

    return True


if __name__ == "__main__":
    try:
        success = backup_all_workspaces()
        if success:
            print("\n🎉 备份成功！所有工作区数据已保护。")
            print("   包含：V2 MVP + 钉钉系统 + 项目管理文档")
        else:
            print("\n❌ 备份失败！请检查错误信息。")
    except Exception as e:
        print(f"\n❌ 备份出错: {e}")
        import traceback
        traceback.print_exc()
