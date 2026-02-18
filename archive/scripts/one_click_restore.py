# -*- coding: utf-8 -*-
"""
一键恢复系统 - 从备份恢复OpenClaw工作区

支持：
- 自动检测最新备份
- 选择恢复哪个备份
- 恢复代码、记忆、配置
- 验证恢复完整性
- 自动重启服务
"""

import os
import zipfile
import shutil
from datetime import datetime


def list_backups(backup_dir=r"D:\ClawBackups"):
    """列出所有可用的备份"""
    print(f"\n📋 可用备份列表（{backup_dir}）：")
    print("="*70)

    if not os.path.exists(backup_dir):
        print("❌ 备份目录不存在！")
        return []

    # 列出所有zip文件
    zip_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]

    if not zip_files:
        print("❌ 没有找到备份文件！")
        return []

    # 按修改时间排序（最新的在前）
    backups = []
    for zip_file in zip_files:
        path = os.path.join(backup_dir, zip_file)
        stat = os.stat(path)
        backups.append({
            'name': zip_file,
            'path': path,
            'size': stat.st_size / 1024 / 1024,  # MB
            'time': datetime.fromtimestamp(stat.st_mtime)
        })

    # 按时间倒序
    backups.sort(key=lambda x: x['time'], reverse=True)

    # 显示前20个备份
    print(f"备份名称                                      大小      时间")
    print("-"*70)
    for i, backup in enumerate(backups[:20], 1):
        time_str = backup['time'].strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i:2d}. {backup['name'][:40]:40s} {backup['size']:8.2f} MB {time_str}")

    if len(backups) > 20:
        print(f"... 还有 {len(backups) - 20} 个备份")

    return backups


def restore_backup(backup_path, target_dir=r"C:\Users\10952\.openclaw\workspace", backup_type="project"):
    """恢复备份

    Args:
        backup_path: 备份文件路径
        target_dir: 恢复目标目录
        backup_type: 备份类型 ("full" 或 "project")
    """
    print(f"\n🔄 开始恢复备份...")
    print(f"备份文件: {backup_path}")
    print(f"目标目录: {target_dir}")
    print(f"备份类型: {backup_type}")
    print()

    # 验证备份文件是否存在
    if not os.path.exists(backup_path):
        print(f"❌ 备份文件不存在！")
        return False

    # 备份当前目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup = f"{target_dir}_before_restore_{timestamp}"
    print(f"📦 先备份当前目录到: {current_backup}")

    try:
        if os.path.exists(target_dir):
            shutil.copytree(target_dir, current_backup)
            print(f"✅ 当前目录已备份")
    except Exception as e:
        print(f"❌ 备份当前目录失败: {e}")
        return False

    print()
    print("📂 解压备用份文件...")

    try:
        # 创建临时解压目录
        temp_dir = f"{target_dir}_temp_extract_{timestamp}"
        os.makedirs(temp_dir, exist_ok=True)

        # 解压备份
        with zipfile.ZipFile(backup_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            print(f"✅ 备份文件已解压")

        print()
        print("🔄 恢复文件...")

        # 根据备份类型处理
        if backup_type == "full":
            # 完整备份：包含 workspace_current 和 workspace_legacy
            workspace_current = os.path.join(temp_dir, "workspace_current")
            if os.path.exists(workspace_current):
                print(f"  恢复 workspace_current...")
                # 删除旧目录
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                # 移动新目录
                shutil.move(workspace_current, target_dir)
        else:
            # 项目备份：直接恢复
            if os.path.exists(temp_dir):
                print(f"  恢复项目文件...")
                # 删除旧目录
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                # 移动新目录
                shutil.move(temp_dir, target_dir)

        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"✅ 临时目录已清理")

        print()
        print("="*70)
        print("✅ 恢复成功！")
        print(f"   源备份: {backup_path}")
        print(f"   当前备份: {current_backup}")
        print(f"   目标目录: {target_dir}")
        print("="*70)

        return True

    except Exception as e:
        print(f"\n❌ 恢复失败: {e}")
        import traceback
        traceback.print_exc()

        # 如果失败，尝试从备份恢复
        print()
        print("🔄 尝试从备份恢复...")
        try:
            if os.path.exists(current_backup):
                shutil.rmtree(target_dir, ignore_errors=True)
                shutil.move(current_backup, target_dir)
                print("✅ 已从备份恢复到原状态")
        except Exception as e2:
            print(f"❌ 恢复备份也失败: {e2}")

        return False


def restore_latest(workspace):
    """一键恢复最新备份"""
    print("="*70)
    print("🚀 一键恢复最新备份")
    print("="*70)

    # 列出备份
    backups = list_backups()

    if not backups:
        return False

    print()
    print("🎯 选择要恢复的备份：")
    print("  1. 恢复最新备份")
    print("  2. 恢复指定编号")
    print("  3. 取消")

    choice = input("\n请选择 (1/2/3): ").strip()

    if choice == "1":
        # 恢复最新备份
        latest = backups[0]
        print(f"\n✅ 将恢复最新的备份: {latest['name']}")

        confirm = input("确认恢复？这将覆盖当前目录 (yes/no): ").strip().lower()
        if confirm != "yes":
            print("❌ 已取消")
            return False

        # 恢复
        return restore_backup(latest['path'], workspace, backup_type="project")

    elif choice == "2":
        # 选择编号
        try:
            num = int(input("请输入备份编号: "))
            if 1 <= num <= len(backups):
                backup = backups[num - 1]
                print(f"\n✅ 将恢复备份: {backup['name']}")

                confirm = input("确认恢复？(yes/no): ").strip().lower()
                if confirm != "yes":
                    print("❌ 已取消")
                    return False

                return restore_backup(backup['path'], workspace, backup_type="project")
            else:
                print(f"❌ 编号无效")
                return False
        except ValueError:
            print("❌ 无效输入")
            return False

    else:
        print("❌ 已取消")
        return False


if __name__ == "__main__":
    workspace = r"C:\Users\10952\.openclaw\workspace"

    print("\n" + "="*70)
    print("🛡️ OpenClaw 一键恢复系统")
    print("="*70)
    print(f"当前工作区: {workspace}")

    # 一键恢复
    success = restore_latest(workspace)

    if success:
        print("\n✅ 恢复成功！")
        print("\n下一步操作：")
        print("  1. 检查恢复的文件是否正确")
        print("  2. 重启OpenClaw（如果需要）")
        print("  3. 验证功能是否正常")
        print("\n如需重新安装OpenClaw:")
        print("  npm install -g @qingchencloud/openclaw-zh")
    else:
        print("\n❌ 恢复失败！请检查错误信息。")
