# 修复 openai.py 添加 MODEL_POOL

with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 DEFAULT_MODEL 和 FALLBACK_MODEL 部分
old_text = '''    DEFAULT_MODEL = "qwen/qwen3.5-397b-a17b"  # ⭐ 397B 参数，Hybrid MoE，更稳定
    FALLBACK_MODEL = "z-ai/glm4.7"  # GLM4.7 备用
    
    # ⭐ 新增：超时配置
    DEFAULT_TIMEOUT = 180.0  # 3 分钟（GLM4.7 可能需要 2-3 分钟）'''

new_text = '''    # ⭐ 多模型池（按优先级排序，自动 fallback）
    MODEL_POOL = [
        "qwen/qwen3.5-397b-a17b",  # 主模型：397B，高质量
        "z-ai/glm4.7",             # 备用模型
    ]
    DEFAULT_MODEL = MODEL_POOL[0]
    FALLBACK_MODEL = MODEL_POOL[1] if len(MODEL_POOL) > 1 else MODEL_POOL[0]
    
    # ⭐ 超时配置
    DEFAULT_TIMEOUT = 180.0  # 3 分钟'''

content = content.replace(old_text, new_text)

with open('v2_learning_system_real/llm/openai.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ MODEL_POOL 添加完成！")
