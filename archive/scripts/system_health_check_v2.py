"""
简化版系统健康检查（修复导入问题后）
"""

import sys
import os

print("=" * 80)
print("🏥 OpenClaw 系统健康检查 v2")
print("=" * 80)

# 1. 检查 API Key 配置（直接读取文件）
print("\n1️⃣ 检查 API Key 配置...")
try:
    with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查 API_KEY_POOL
    if 'API_KEY_POOL = [' in content:
        print("  ✅ API_KEY_POOL 存在")
        # 提取 keys
        import re
        keys = re.findall(r'"(nvapi-[^"]+)"', content)
        print(f"  🔑 Key 数量：{len(keys)}")
        for i, key in enumerate(keys):
            masked = key[:8] + "..." + key[-6:]
            print(f"     {i+1}. {masked}")
    else:
        print("  ❌ API_KEY_POOL 未找到")
    
    # 检查 MODEL_POOL
    if 'MODEL_POOL = [' in content:
        print("  ✅ MODEL_POOL 存在")
        models = re.findall(r'"([^"]+)"', content.split('MODEL_POOL = [')[1].split(']')[0])
        print(f"  📋 模型数量：{len(models)}")
        for i, model in enumerate(models):
            marker = "⭐" if i == 0 else "  "
            print(f"     {marker} {model}")
    else:
        print("  ❌ MODEL_POOL 未找到")
    
    # 检查 fallback 方法
    if 'learning_with_fallback' in content:
        print("  ✅ learning_with_fallback 方法存在")
    else:
        print("  ❌ learning_with_fallback 方法未找到")
    
    # 检查 switch_api_key 方法
    if 'switch_api_key' in content:
        print("  ✅ switch_api_key 方法存在")
    else:
        print("  ❌ switch_api_key 方法未找到")
    
except Exception as e:
    print(f"  ❌ 检查失败：{e}")

# 2. 测试初始化（直接导入类）
print("\n2️⃣ 测试初始化（不传 api_key 参数）...")
try:
    sys.path.insert(0, 'v2_learning_system_real/llm')
    from openai import OpenAIProvider
    
    provider = OpenAIProvider()
    print(f"  ✅ 默认初始化成功")
    print(f"     当前模型：{provider.model}")
    print(f"     当前 API Key 索引：{provider.api_key_index}")
    print(f"     超时设置：{provider.timeout}秒")
except Exception as e:
    print(f"  ❌ 初始化失败：{e}")
    import traceback
    traceback.print_exc()

# 3. 检查 MVP JARVIS 组件
print("\n3️⃣ 检查 MVP JARVIS 组件...")
try:
    sys.path.insert(0, 'mvp_jarvais')
    from core.memory_manager import MemoryManager
    print(f"  ✅ MemoryManager 导入成功")
except Exception as e:
    print(f"  ⚠️ MemoryManager 导入失败：{e}")

try:
    from core.tool_engine import ToolEngine
    print(f"  ✅ ToolEngine 导入成功")
except Exception as e:
    print(f"  ⚠️ ToolEngine 导入失败：{e}")

try:
    from agents.knowledge_agent import KnowledgeAgent
    print(f"  ✅ KnowledgeAgent 导入成功")
except Exception as e:
    print(f"  ⚠️ KnowledgeAgent 导入失败：{e}")

# 4. 检查 TaskLogger
print("\n4️⃣ 检查 TaskLogger...")
try:
    from task_logger import TaskLogger
    # 直接实例化
    logger = TaskLogger()
    print(f"  ✅ TaskLogger 初始化成功")
    print(f"     日志文件：{logger.log_file}")
except Exception as e:
    print(f"  ❌ TaskLogger 初始化失败：{e}")

# 5. 检查 Gateway 服务
print("\n5️⃣ 检查 Gateway 服务...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8001))
    if result == 0:
        print(f"  ✅ Gateway 服务运行中（端口 8001）")
    else:
        print(f"  ⚠️ Gateway 服务未运行（端口 8001 未监听）")
    sock.close()
except Exception as e:
    print(f"  ⚠️ 检查失败：{e}")

print("\n" + "=" * 80)
print("✅ 健康检查完成！")
print("=" * 80)
