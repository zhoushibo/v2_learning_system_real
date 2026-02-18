"""手动测试三层记忆系统初始化"""
import os
import sqlite3

# 创建数据库目录
db_dir = r'C:\Users\10952\.openclaw\workspace\memory'
os.makedirs(db_dir, exist_ok=True)

# 数据库路径
db_path = os.path.join(db_dir, 'v1_memory.db')

print(f"数据库目录: {db_dir}")
print(f"数据库路径: {db_path}")
print(f"目录是否存在: {os.path.exists(db_dir)}")

# 初始化SQLite
try:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    # 创建任务表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            result TEXT,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT DEFAULT '{}'
        )
    ''')

    conn.commit()

    # 测试插入
    import json
    from datetime import datetime

    test_task_id = "test_manual_001"
    cursor.execute('''
        INSERT OR REPLACE INTO tasks
        (task_id, content, status, result, error, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        test_task_id,
        "手动测试任务",
        "completed",
        "测试成功",
        None,
        json.dumps({"test": True}, ensure_ascii=False)
    ))
    conn.commit()

    # 查询测试
    cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (test_task_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    data = dict(zip(columns, row))

    print("\n✅ SQLite初始化成功！")
    print(f"任务数据: {data}")

    conn.close()

except Exception as e:
    print(f"❌ SQLite初始化失败: {e}")
    import traceback
    traceback.print_exc()
