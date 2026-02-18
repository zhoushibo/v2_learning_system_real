# -*- coding: utf-8 -*-
"""快速备份工作区到D盘"""
import shutil
import os
import zipfile
from datetime import datetime


def backup_to_d_drive():
    """备份工作区到D盘"""

    # 源目录和目标目录
    source_dir = r"C:\Users\10952\.openclaw\workspace"
    backup_dir = r"D:\ClawBackups"

    # 创建备份目录
    os.makedirs(backup_dir, exist_ok=True)

    # 生成备份名称（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"WORKSPACE_BACKUP_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)

    print("="*70)
    print("🔧 开始备份工作区到D盘")
    print("="*70)
    print(f"源目录: {source_dir}")
    print(f"备份位置: {backup_path}")
    print()

    # 创建压缩文件
    zip_name = f"{backup_path}.zip"

    print("📦 正在压缩... (这可能需要几分钟)")
    print()

    # 排除的文件和目录
    exclude = [
        '__pycache__',
        '.git',
        '*.pyc',
        '*.pyd',
        '*.log',
        '*.tmp',
        '*.swp',
        'node_modules',
        # 可以根据需要添加更多排除项
    ]

    # 开始压缩
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total_files = 0
        for root, dirs, files in os.walk(source_dir):
            # 移除排除的目录
            dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude)]

            for file in files:
                # 排除文件
                if any(ex in file for ex in exclude):
                    continue

                file_path = os.path.join(root, file)
                # 计算相对路径
                rel_path = os.path.relpath(file_path, source_dir)

                # 添加到压缩文件
                zipf.write(file_path, rel_path)
                total_files += 1

                # 显示进度
                if total_files % 100 == 0:
                    print(f"  已压缩: {total_files} 个文件...", end='\r')

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
        f.write(f"工作区备份信息\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"源目录: {source_dir}\n")
        f.write(f"备份文件: {zip_name}\n")
        f.write(f"文件数量: {total_files}\n")
        f.write(f"文件大小: {os.path.getsize(zip_name) / 1024 / 1024:.2f} MB\n")
        f.write(f"\n包含内容:\n")
        f.write(f"  - openclaw_async_architecture/ (V2 MVP)\n")
        f.write(f"  - memory/ (记忆系统)\n")
        f.write(f"  - *.md 文档\n")
        f.write(f"  - 测试脚本\n")

    print(f"📝 备份信息已保存: {info_file}")
    print()
    print("="*70)
    print("✅ 备份完成！")
    print("="*70)

    return True


if __name__ == "__main__":
    try:
        success = backup_to_d_drive()
        if success:
            print("\n🎉 备份成功！数据已保护。")
        else:
            print("\n❌ 备份失败！请检查错误信息。")
    except Exception as e:
        print(f"\n❌ 备份出错: {e}")
        import traceback
        traceback.print_exc()
