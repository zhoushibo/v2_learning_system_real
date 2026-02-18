"""
精确修复 openai.py 的 api_key 初始化顺序问题
"""

# 读取文件
with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到需要修复的行
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # 找到这一行：self.api_key_index = self.API_KEY_POOL.index(api_key) if api_key in self.API_KEY_POOL else 0
    if 'self.api_key_index = self.API_KEY_POOL.index(api_key)' in line and 'if api_key in self.API_KEY_POOL' in line:
        # 检查前一行是否有 api_key=None 的检查
        prev_line = lines[i-1] if i > 0 else ""
        
        if 'if api_key is None:' not in prev_line and 'api_key = self.API_KEY_POOL[0]' not in prev_line:
            # 需要在这里插入 api_key=None 检查
            indent = '        '  # 8 个空格
            fixed_lines.append(f"{indent}# ⭐ 修复：确保 api_key 始终有值（在 super() 之后）\n")
            fixed_lines.append(f"{indent}if api_key is None:\n")
            fixed_lines.append(f"{indent}    api_key = self.API_KEY_POOL[0]\n")
            fixed_lines.append(f"{indent}\n")
    
    fixed_lines.append(line)
    i += 1

# 写回文件
with open('v2_learning_system_real/llm/openai.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ 修复完成！")
print("\n已添加 api_key=None 检查，确保初始化时始终有有效的 API Key")
