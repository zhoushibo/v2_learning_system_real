# 添加 API_KEY_POOL 到类定义开头

with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 class OpenAIProvider(LLMProvider): 这一行
new_lines = []
inserted = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # 在 class 定义后立即插入 API_KEY_POOL
    if 'class OpenAIProvider(LLMProvider):' in line and not inserted:
        new_lines.append('\n')
        new_lines.append('    # ⭐ API Key 池（负载均衡 + 自动切换）\n')
        new_lines.append('    API_KEY_POOL = [\n')
        new_lines.append('        "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",  # 主 Key\n')
        new_lines.append('        "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",  # 备用 Key\n')
        new_lines.append('    ]\n')
        inserted = True

with open('v2_learning_system_real/llm/openai.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ API_KEY_POOL 添加到类定义！")

# 验证
with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'API_KEY_POOL = [' in content:
        print("✅ 验证成功：API_KEY_POOL 已添加")
    else:
        print("❌ 验证失败：API_KEY_POOL 未找到")
