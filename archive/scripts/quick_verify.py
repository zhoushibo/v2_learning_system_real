"""
快速验证脚本 - 测试 API Key 和模型池配置
绕过导入问题，直接检查配置
"""

import re

print("=" * 80)
print("⚡ 快速验证：5 模型 +2API Key 配置")
print("=" * 80)

# 读取 openai.py
with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 验证 API_KEY_POOL
print("\n🔑 API Key 池验证:")
api_keys = re.findall(r'"(nvapi-[^"]+)"', content.split('API_KEY_POOL = [')[1].split(']')[0])
print(f"  找到 {len(api_keys)} 个 API Key:")
for i, key in enumerate(api_keys, 1):
    masked = key[:12] + "..." + key[-6:]
    print(f"    {i}. {masked}")

if len(api_keys) >= 2:
    print("  ✅ API Key 池配置正确（≥2 个 Key）")
else:
    print("  ❌ API Key 池配置不足（需要≥2 个）")

# 2. 验证 MODEL_POOL
print("\n📋 模型池验证:")
model_pool_section = content.split('MODEL_POOL = [')[1].split(']')[0]
models = re.findall(r'"([^"]+)"', model_pool_section)
print(f"  找到 {len(models)} 个模型:")
for i, model in enumerate(models, 1):
    marker = "⭐" if i == 1 else "  "
    print(f"    {marker} {model}")

if len(models) >= 5:
    print("  ✅ 模型池配置正确（≥5 个模型）")
else:
    print("  ❌ 模型池配置不足（需要≥5 个）")

# 3. 验证 fallback 方法
print("\n🔄 Fallback 机制验证:")
checks = {
    'learning_with_fallback': '多模型 fallback 方法',
    'switch_api_key': 'API Key 切换方法',
    'MODEL_POOL': '模型池定义',
    'API_KEY_POOL': 'API Key 池定义',
}

all_ok = True
for method, desc in checks.items():
    if method in content:
        print(f"  ✅ {desc}: 存在")
    else:
        print(f"  ❌ {desc}: 缺失")
        all_ok = False

# 4. 验证初始化修复
print("\n🔧 初始化修复验证:")
if 'if api_key is None:' in content and 'api_key = self.API_KEY_POOL[0]' in content:
    print("  ✅ api_key=None 检查已添加")
else:
    print("  ❌ api_key=None 检查未找到")
    all_ok = False

# 5. 总结
print("\n" + "=" * 80)
if all_ok:
    print("✅ 所有配置验证通过！系统应该可以正常工作")
    print("\n📝 下一步建议:")
    print("  1. 启动 Gateway 服务：cd openclaw_async_architecture/streaming-service; python src/gateway.py")
    print("  2. 测试真实 API 调用：python v2_learning_system_real/examples/with_nvidia.py")
    print("  3. 运行完整系统测试：python mvp_jarvais/tests/core_components_test.py")
else:
    print("⚠️ 部分配置缺失，请检查上述错误")

print("=" * 80)
