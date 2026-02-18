"""
修复 api_key 初始化顺序问题
问题：api_key_index 赋值在 api_key=None 检查之前
解决：先确保 api_key 有值，再计算 api_key_index
"""

import re

# 读取文件
with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 __init__ 方法并修复
old_init = '''    def __init__(self, api_key: str = None, model: str = None, base_url: str = None, max_tokens: int = None, timeout: float = None):
        """
        初始化 OpenAI 提供者
        Args:
            api_key: OpenAI API 密钥
            model: 模型名称（默认：gpt-4）
            base_url: 自定义 base_url（如 NVIDIA API）
            max_tokens: 最大输出 tokens（GLM4.7 建议 4000-8000）
            timeout: 超时时间（秒，默认 180 秒）
        """
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self.base_url = base_url
        self.api_key_index = self.API_KEY_POOL.index(api_key) if api_key in self.API_KEY_POOL else 0
        self.timeout = timeout or self.DEFAULT_TIMEOUT'''

new_init = '''    def __init__(self, api_key: str = None, model: str = None, base_url: str = None, max_tokens: int = None, timeout: float = None):
        """
        初始化 OpenAI 提供者
        Args:
            api_key: OpenAI API 密钥（默认使用 API_KEY_POOL[0]）
            model: 模型名称（默认：gpt-4）
            base_url: 自定义 base_url（如 NVIDIA API）
            max_tokens: 最大输出 tokens（GLM4.7 建议 4000-8000）
            timeout: 超时时间（秒，默认 180 秒）
        """
        # ⭐ 修复：确保 api_key 始终有值（在 super() 之前）
        if api_key is None:
            api_key = self.API_KEY_POOL[0]
        
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self.base_url = base_url
        self.api_key_index = self.API_KEY_POOL.index(api_key) if api_key in self.API_KEY_POOL else 0
        self.timeout = timeout or self.DEFAULT_TIMEOUT'''

if old_init in content:
    content = content.replace(old_init, new_init)
    with open('v2_learning_system_real/llm/openai.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 修复成功！api_key 初始化顺序已修正")
else:
    print("⚠️ 未找到匹配的旧代码，尝试另一种格式...")
    # 尝试更宽松的匹配
    if 'self.api_key_index = self.API_KEY_POOL.index(api_key) if api_key in self.API_KEY_POOL else 0' in content:
        print("  找到 api_key_index 赋值语句")
        # 显示上下文
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'self.api_key_index' in line:
                print(f"  第{i+1}行：{line}")
                print(f"  前一行：{lines[i-1] if i > 0 else 'N/A'}")
                print(f"  后一行：{lines[i+1] if i < len(lines) else 'N/A'}")
