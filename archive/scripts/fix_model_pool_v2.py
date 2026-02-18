# 精确替换 MODEL_POOL

with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 DEFAULT_MODEL 行并替换
new_lines = []
for i, line in enumerate(lines):
    if 'DEFAULT_MODEL = "qwen/qwen3.5-397b-a17b"' in line:
        # 插入 MODEL_POOL
        new_lines.append('    # ⭐ 多模型池（自动 fallback）\n')
        new_lines.append('    MODEL_POOL = [\n')
        new_lines.append('        "qwen/qwen3.5-397b-a17b",  # 主模型\n')
        new_lines.append('        "z-ai/glm4.7",             # 备用模型\n')
        new_lines.append('    ]\n')
        new_lines.append('    DEFAULT_MODEL = MODEL_POOL[0]\n')
        new_lines.append('    FALLBACK_MODEL = MODEL_POOL[1] if len(MODEL_POOL) > 1 else MODEL_POOL[0]\n')
        # 跳过原来的 FALLBACK_MODEL 行
    elif 'FALLBACK_MODEL = "z-ai/glm4.7"' in line:
        # 跳过这一行
        continue
    else:
        new_lines.append(line)

with open('v2_learning_system_real/llm/openai.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ MODEL_POOL 添加完成！")
print("验证：检查文件内容...")

with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[38:50], start=39):
        print(f"{i}: {line}", end='')
