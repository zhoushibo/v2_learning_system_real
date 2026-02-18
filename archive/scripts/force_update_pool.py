# 强制更新 MODEL_POOL 为 5 个模型

with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 MODEL_POOL 开始和结束
new_lines = []
in_model_pool = False
model_pool_added = False

for i, line in enumerate(lines):
    if 'MODEL_POOL = [' in line and not model_pool_added:
        # 开始替换
        in_model_pool = True
        new_lines.append('    MODEL_POOL = [\n')
        new_lines.append('        "qwen/qwen3.5-397b-a17b",              # 主模型，397B\n')
        new_lines.append('        "z-ai/glm5",                           # 最新 GLM-5\n')
        new_lines.append('        "moonshotai/kimi-k2.5",                # Kimi K2.5\n')
        new_lines.append('        "qwen/qwen3-next-80b-a3b-instruct",    # Qwen3-Next 80B\n')
        new_lines.append('        "z-ai/glm4.7",                         # 备用 GLM-4.7\n')
        continue
    elif in_model_pool:
        if ']' in line:
            # 结束替换
            in_model_pool = False
            model_pool_added = True
            new_lines.append('    ]\n')
        # 跳过旧行
        continue
    else:
        new_lines.append(line)

with open('v2_learning_system_real/llm/openai.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✅ 强制替换完成！')
print('新 MODEL_POOL: 5 个模型')
