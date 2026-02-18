import re

# 读取文件
with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 替换默认模型
content = content.replace(
    'DEFAULT_MODEL = "gpt-4"',
    'DEFAULT_MODEL = "qwen/qwen3.5-397b-a17b"  # ⭐ 397B 参数，Hybrid MoE，更稳定'
)
content = content.replace(
    'FALLBACK_MODEL = "gpt-3.5-turbo"',
    'FALLBACK_MODEL = "z-ai/glm4.7"  # GLM4.7 备用'
)

# 2. 替换 max_tokens 配置（针对 Qwen3.5 优化）
old_code = '''if "glm" in (model or "").lower():
            self.max_tokens = 8000 if max_tokens is None else max(max_tokens, 4000)
        else:
            self.max_tokens = max_tokens or 2000'''

new_code = '''# 针对不同模型调整 max_tokens
        model_lower = (model or "").lower()
        if "glm" in model_lower:
            self.max_tokens = 8000 if max_tokens is None else max(max_tokens, 4000)
        elif "qwen" in model_lower:
            # Qwen3.5 支持 262K 上下文，推荐 max_tokens=16384
            self.max_tokens = 16384 if max_tokens is None else max(max_tokens, 8000)
        else:
            self.max_tokens = max_tokens or 2000'''

content = content.replace(old_code, new_code)

# 写回文件
with open('v2_learning_system_real/llm/openai.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 更新完成！')
print('新默认模型：qwen/qwen3.5-397b-a17b')
print('Qwen3.5 max_tokens: 16384')
print('GLM4.7 max_tokens: 8000')
