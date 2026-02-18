# 最终清理：移动所有 .py 脚本到 archive/scripts/
import os
import shutil

workspace = 'C:/Users/10952/.openclaw/workspace'
archive_scripts = os.path.join(workspace, 'archive', 'scripts')

# 创建 archive/scripts/
os.makedirs(archive_scripts, exist_ok=True)

# 核心脚本（保留在根目录）
core_scripts = {
    'start_all.py',  # 可能常用
}

moved_count = 0
moved_size = 0

for item in os.listdir(workspace):
    item_path = os.path.join(workspace, item)
    
    # 跳过目录
    if os.path.isdir(item_path):
        continue
    
    # 只处理 .py 文件
    if not item.endswith('.py'):
        continue
    
    # 跳过核心脚本
    if item in core_scripts:
        print(f'✅ 保留：{item}')
        continue
    
    # 移动
    try:
        file_size = os.path.getsize(item_path)
        shutil.move(item_path, os.path.join(archive_scripts, item))
        print(f'📦 移动：{item} ({file_size:,} 字符)')
        moved_count += 1
        moved_size += file_size
    except Exception as e:
        print(f'❌ 失败：{item} - {e}')

print(f'\n=== 完成 ===')
print(f'📦 移动：{moved_count} 个文件')
print(f'📉 减少：{moved_size:,} 字符（{moved_size/1000:.1f}K）')
