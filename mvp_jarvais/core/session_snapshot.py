# -*- coding: utf-8 -*-
"""
Session Snapshot Manager
实现会话的自动保存和恢复，确保 100% 会话连续性
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class SessionSnapshotManager:
    """会话快照管理器"""
    
    def __init__(self, workspace: str = None):
        if workspace is None:
            # 使用 POSIX 路径格式
            workspace = "C:/Users/10952/.openclaw/workspace"
        
        self.workspace = Path(workspace)
        self.state_file = self.workspace / "STATE.json"
        self.state_backup_dir = self.workspace / ".state_backups"
        self.memory_dir = self.workspace / "memory"
        self.memory_file = self.workspace / "MEMORY.md"
        
        # 确保备份目录存在
        self.state_backup_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def save_snapshot(self, data: Dict[str, Any], atomic: bool = True) -> bool:
        """保存会话快照（原子写入）"""
        try:
            # 添加时间戳
            data['last_updated'] = datetime.now().isoformat()
            
            if atomic:
                # 原子写入：先写临时文件
                temp_file = self.state_file.with_suffix('.json.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 验证写入成功
                with open(temp_file, 'r', encoding='utf-8') as f:
                    verify_data = json.load(f)
                
                # 验证通过，原子替换
                shutil.move(str(temp_file), str(self.state_file))
                
                # 创建备份
                self._rotate_backups()
                
            else:
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ 保存会话快照失败：{e}")
            return False
    
    def load_snapshot(self) -> Optional[Dict[str, Any]]:
        """加载会话快照"""
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
            
        except Exception as e:
            print(f"⚠️ 加载会话快照失败：{e}")
            return self._recover_from_backup()
    
    def _rotate_backups(self, keep: int = 3):
        """轮转备份文件（保留最近 N 个版本）"""
        backup_file = self.state_backup_dir / "STATE.json.bak1"
        
        if self.state_file.exists():
            # 删除最旧的备份
            oldest_backup = self.state_backup_dir / f"STATE.json.bak{keep}"
            if oldest_backup.exists():
                oldest_backup.unlink()
            
            # 轮转现有备份
            for i in range(keep - 1, 0, -1):
                src = self.state_backup_dir / f"STATE.json.bak{i}"
                dst = self.state_backup_dir / f"STATE.json.bak{i + 1}"
                if src.exists():
                    shutil.move(str(src), str(dst))
            
            # 创建新备份
            shutil.copy2(str(self.state_file), str(backup_file))
    
    def _recover_from_backup(self) -> Optional[Dict[str, Any]]:
        """从备份恢复"""
        for i in range(1, 4):
            backup_file = self.state_backup_dir / f"STATE.json.bak{i}"
            if backup_file.exists():
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    continue
        
        return None
    
    def get_status_summary(self) -> str:
        """获取状态摘要"""
        data = self.load_snapshot()
        
        if not data:
            return "⚠️ 未找到会话快照，这是新会话"
        
        last_updated = data.get('last_updated', '未知')
        current_stage = data.get('current_stage', '未知')
        completion = data.get('completion_percentage', 0)
        
        try:
            dt = datetime.fromisoformat(last_updated)
            last_updated_str = dt.strftime('%Y-%m-%d %H:%M')
        except:
            last_updated_str = last_updated
        
        summary = f"""
=== ⚡ 工作状态恢复 ===
📅 最后更新：{last_updated_str}
🎯 当前阶段：{current_stage}
   - 完成度：{completion}%

✅ 最近完成：
"""
        
        projects = data.get('projects', {})
        for proj_name, proj_info in list(projects.items())[:3]:
            status = proj_info.get('status', '未知')
            completion = proj_info.get('completion', 0)
            summary += f"   - {proj_name}: {status} ({completion}%)\n"
        
        next_steps = data.get('next_steps', [])
        if next_steps:
            summary += f"\n📋 下一步：\n"
            for step in next_steps[:3]:
                summary += f"   - {step}\n"
        
        summary += f"\n📄 详细记录：memory/2026-02-18.md"
        
        return summary
    
    def get_latest_memory_file(self) -> Optional[Path]:
        """获取最新的记忆文件"""
        if not self.memory_dir.exists():
            return None
        
        memory_files = list(self.memory_dir.glob("*.md"))
        if not memory_files:
            return None
        
        memory_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return memory_files[0]
    
    def get_session_context(self) -> Dict[str, Any]:
        """获取完整的会话上下文"""
        context = {
            'state': self.load_snapshot(),
            'latest_memory_file': None,
            'latest_memory_content': None,
            'memory_content': None,
        }
        
        latest_memory = self.get_latest_memory_file()
        if latest_memory:
            context['latest_memory_file'] = str(latest_memory)
            try:
                with open(latest_memory, 'r', encoding='utf-8') as f:
                    context['latest_memory_content'] = f.read()
            except:
                pass
        
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    context['memory_content'] = f.read()
            except:
                pass
        
        return context


def main():
    """测试会话快照管理器"""
    print("=" * 70)
    print("🧪 会话快照管理器测试")
    print("=" * 70)
    
    manager = SessionSnapshotManager()
    
    # 测试 1：加载现有快照
    print("\n1️⃣ 加载现有会话快照...")
    snapshot = manager.load_snapshot()
    if snapshot:
        print(f"   ✅ 加载成功：{snapshot.get('current_stage', '未知')}")
    else:
        print("   ⚠️ 未找到现有快照")
    
    # 测试 2：显示状态摘要
    print("\n2️⃣ 状态摘要...")
    summary = manager.get_status_summary()
    print(summary)
    
    # 测试 3：获取会话上下文
    print("\n3️⃣ 获取会话上下文...")
    context = manager.get_session_context()
    print(f"   ✅ STATE.json: {'已加载' if context['state'] else '未找到'}")
    print(f"   ✅ 最新记忆文件：{context['latest_memory_file'] or '无'}")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
