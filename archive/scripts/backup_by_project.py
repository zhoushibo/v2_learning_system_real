# -*- coding: utf-8 -*-
"""项目化备份脚本 - 每个项目单独保存到D盘备份目录"""
import shutil
import os
import zipfile
from datetime import datetime


def backup_single_project(source_path, backup_name, backup_dir, exclude_patterns=None):
    """备份单个项目"""
    if exclude_patterns is None:
        exclude_patterns = ['__pycache__', '*.pyc', '*.pyd', '*.log', '*.tmp',
                           '*.swp', 'node_modules', '.git', '*.db', '*.sqlite']

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"{backup_dir}/{backup_name}_{timestamp}.zip"

    print(f"  📁 备份: {backup_name}")
    print(f"      源: {source_path}")
    print(f"      备份到: {zip_name}")

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total_files = 0
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude_patterns)]
            for file in files:
                if any(ex in file for ex in exclude_patterns):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_path)
                zipf.write(file_path, rel_path)
                total_files += 1
                if total_files % 100 == 0:
                    print(f"      进度: {total_files} 个文件...", end='\r')

    print(f"  ✅ 完成: {total_files} 个文件, {os.path.getsize(zip_name) / 1024 / 1024:.2f} MB")

    # 创建信息文件
    info_file = f"{backup_dir}/{backup_name}_info_{timestamp}.txt"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(f"{backup_name} 备份信息\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"源路径: {source_path}\n")
        f.write(f"备份文件: {zip_name}\n")
        f.write(f"文件数量: {total_files}\n")
        f.write(f"文件大小: {os.path.getsize(zip_name) / 1024 / 1024:.2f} MB\n")

    return zip_name, total_files, os.path.getsize(zip_name)


def main():
    """主函数 - 备份所有项目"""

    backup_base_dir = r"D:\ClawBackups"
    os.makedirs(backup_base_dir, exist_ok=True)

    print("="*70)
    print("🗂️  项目化备份开始")
    print("="*70)
    print(f"备份目录: {backup_base_dir}")
    print()

    # 定义所有项目
    projects = [
        {
            "name": "project_v2_mvp",
            "display_name": "V2 MVP - 异步架构",
            "source": r"C:\Users\10952\.openclaw\workspace\openclaw_async_architecture",
            "description": "OpenClaw V2异步架构MVP项目，包含Gateway、Worker、多模型策略"
        },
        {
            "name": "project_memory_system",
            "display_name": "记忆系统",
            "source": r"C:\Users\10952\.openclaw\workspace\memory",
            "description": "三层记忆系统，包含短期记忆和SQLite数据库"
        },
        {
            "name": "project_documentation",
            "display_name": "核心文档",
            "source": r"C:\Users\10952\.openclaw\workspace",
            "description": "核心文档（README, TODO, PROJECT_LIST等）",
            "files": True,  # 备份特定文件
            "file_patterns": ["*.md", "PROJECT_*.py"]
        },
        {
            "name": "project_dingtalk_agent",
            "display_name": "钉钉AI Agent",
            "source": r"D:\.openclaw\workspace\claw_agent_demo",
            "description": "钉钉AI Agent系统，包含加解密、Flask服务器、钉钉适配器"
        },
        {
            "name": "project_novel_tools",
            "display_name": "小说工具",
            "source": r"D:\.openclaw\workspace\novel_tools",
            "description": "小说创作工具集"
        },
        {
            "name": "project_pipelines",
            "display_name": "工具流水线",
            "source": r"D:\.openclaw\workspace\pipelines",
            "description": "工具流水线和脚本"
        },
        {
            "name": "project_tools",
            "display_name": "工具集",
            "source": r"D:\.openclaw\workspace\tools",
            "description": "通用工具集"
        },
        {
            "name": "project_agents_legacy",
            "display_name": "钉钉代理系统",
            "source": r"D:\.openclaw\workspace\agents",
            "description": "钉钉代理系统（旧版）"
        },
        {
            "name": "project_openclaw_v2_legacy",
            "display_name": "OpenClaw V2（实验版）",
            "source": r"D:\.openclaw\workspace\openclaw_v2",
            "description": "OpenClaw V2实验性版本"
        }
    ]

    # 备份统计
    backup_summary = []

    # 遍历所有项目
    for project in projects:
        if not os.path.exists(project["source"]):
            print(f"  ⚠️  跳过: {project['display_name']} (不存在)")
            backup_summary.append({
                "name": project["display_name"],
                "status": "跳过",
                "reason": "不存在"
            })
            continue

        try:
            # 备份项目
            zip_path, file_count, size = backup_single_project(
                source_path=project["source"],
                backup_name=project["name"],
                backup_dir=backup_base_dir
            )

            backup_summary.append({
                "name": project["display_name"],
                "status": "成功",
                "files": file_count,
                "size": f"{size / 1024 / 1024:.2f} MB",
                "path": zip_path
            })

            print()

        except Exception as e:
            print(f"  ❌ 失败: {e}")
            backup_summary.append({
                "name": project["display_name"],
                "status": "失败",
                "reason": str(e)
            })
            print()

    # 生成汇总报告
    print("="*70)
    print("📊 备份汇总")
    print("="*70)

    total_projects = len(backup_summary)
    success_count = sum(1 for s in backup_summary if s["status"] == "成功")
    failed_count = sum(1 for s in backup_summary if s["status"] == "失败")
    skipped_count = sum(1 for s in backup_summary if s["status"] == "跳过")

    print(f"\n总计项目: {total_projects}")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {failed_count}")
    print(f"⏭️  跳过: {skipped_count}")

    print(f"\n{'项目名称':<25} {'状态':<8} {'文件数':<10} {'大小':<12}")
    print(f"{'-'*70}")

    for summary in backup_summary:
        if summary["status"] == "成功":
            print(f"{summary['name']:<25} ✅ {summary['status']:<6} {summary['files']:<10} {summary['size']:<12}")
        elif summary["status"] == "跳过":
            print(f"{summary['name']:<25} ⏭️  {summary['status']:<6} {summary['reason']:<22}")
        else:
            print(f"{summary['name']:<25} ❌ {summary['status']:<6} {summary['reason']:<22}")

    # 保存汇总报告
    summary_file = f"{backup_base_dir}/BACKUP_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"项目化备份汇总报告\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总计项目: {total_projects}\n")
        f.write(f"成功: {success_count}\n")
        f.write(f"失败: {failed_count}\n")
        f.write(f"跳过: {skipped_count}\n\n")

        f.write(f"项目明细:\n")
        f.write(f"{'-'*70}\n")
        for project in projects:
            f.write(f"\n项目: {project['display_name']}\n")
            f.write(f"  源路径: {project['source']}\n")
            f.write(f"  描述: {project['description']}\n")

        f.write(f"\n\n备份结果:\n")
        f.write(f"{'-'*70}\n")
        for summary in backup_summary:
            f.write(f"\n项目: {summary['name']}\n")
            f.write(f"  状态: {summary['status']}\n")
            if summary["status"] == "成功":
                f.write(f"  文件数: {summary['files']}\n")
                f.write(f"  大小: {summary['size']}\n")
                f.write(f"  备份文件: {summary['path']}\n")
            else:
                f.write(f"  原因: {summary['reason']}\n")

    print(f"\n📝 汇总报告已保存: {summary_file}")
    print()
    print("="*70)
    print("🎉 项目化备份完成！")
    print("="*70)
    print(f"\n所有项目已单独保存到: {backup_base_dir}")
    print(f"\n每个项目格式: 项目名_时间戳.zip")

    return True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 备份过程出错: {e}")
        import traceback
        traceback.print_exc()
