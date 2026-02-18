"""
OpenClaw 系统健康检查
快速诊断常见问题：API Key、模型池、初始化、连接性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🏥 OpenClaw 系统健康检查")
print("=" * 80)

# 1. 检查文件存在性
print("\n1️⃣ 检查核心文件...")
files_to_check = [
    'v2_learning_system_real/llm/openai.py',
    'v2_learning_system_real/llm/base.py',
    'mvp_jarvais/core/memory_manager.py',
    'mvp_jarvais/core/tool_engine.py',
    'task_logger.py',
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} - 文件不存在！")

# 2. 检查 API Key 配置
print("\n2️⃣ 检查 API Key 配置...")
try:
    from v2_learning_system_real.llm.openai import OpenAIProvider
    
    print(f"  ✅ OpenAIProvider 导入成功")
    print(f"  🔑 API_KEY_POOL 大小：{len(OpenAIProvider.API_KEY_POOL)}")
    for i, key in enumerate(OpenAIProvider.API_KEY_POOL):
        masked = key[:8] + "..." + key[-6:]
        print(f"     {i+1}. {masked}")
    
    print(f"  📋 MODEL_POOL 大小：{len(OpenAIProvider.MODEL_POOL)}")
    for i, model in enumerate(OpenAIProvider.MODEL_POOL):
        marker = "⭐" if i == 0 else "  "
        print(f"     {marker} {model}")
    
except Exception as e:
    print(f"  ❌ 导入失败：{e}")
    import traceback
    traceback.print_exc()

# 3. 测试初始化（不传 api_key）
print("\n3️⃣ 测试初始化（不传 api_key 参数）...")
try:
    provider = OpenAIProvider()
    print(f"  ✅ 默认初始化成功")
    print(f"     当前模型：{provider.model}")
    print(f"     当前 API Key 索引：{provider.api_key_index}")
    print(f"     超时设置：{provider.timeout}秒")
except Exception as e:
    print(f"  ❌ 初始化失败：{e}")
    import traceback
    traceback.print_exc()

# 4. 测试初始化（传入 api_key）
print("\n4️⃣ 测试初始化（传入 api_key 参数）...")
try:
    test_key = OpenAIProvider.API_KEY_POOL[0]
    provider2 = OpenAIProvider(api_key=test_key)
    print(f"  ✅ 指定 Key 初始化成功")
    print(f"     API Key 索引：{provider2.api_key_index}")
except Exception as e:
    print(f"  ❌ 初始化失败：{e}")
    import traceback
    traceback.print_exc()

# 5. 检查 MVP JARVIS 组件
print("\n5️⃣ 检查 MVP JARVIS 组件...")
try:
    from mvp_jarvais.core.memory_manager import MemoryManager
    print(f"  ✅ MemoryManager 导入成功")
except Exception as e:
    print(f"  ⚠️ MemoryManager 导入失败：{e}")

try:
    from mvp_jarvais.core.tool_engine import ToolEngine
    print(f"  ✅ ToolEngine 导入成功")
except Exception as e:
    print(f"  ⚠️ ToolEngine 导入失败：{e}")

try:
    from mvp_jarvais.agents.knowledge_agent import KnowledgeAgent
    print(f"  ✅ KnowledgeAgent 导入成功")
except Exception as e:
    print(f"  ⚠️ KnowledgeAgent 导入失败：{e}")

# 6. 检查任务日志器
print("\n6️⃣ 检查任务日志器...")
try:
    from task_logger import TaskLogger
    logger = TaskLogger.get_instance()
    print(f"  ✅ TaskLogger 初始化成功")
    print(f"     日志文件：{logger.log_file}")
except Exception as e:
    print(f"  ❌ TaskLogger 初始化失败：{e}")

# 7. 快速连接性测试
print("\n7️⃣ 快速连接性测试（可选，按 Ctrl+C 跳过）...")
print("  跳过（需要 API 调用）")

print("\n" + "=" * 80)
print("✅ 健康检查完成！")
print("=" * 80)
