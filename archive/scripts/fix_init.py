# 修复 __init__ 让 api_key 可选

with open('v2_learning_system_real/llm/openai.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 __init__ 签名和文档
old_init = '''    def __init__(self, api_key: str, model: str = None, base_url: str = None, max_tokens: int = None, timeout: float = None):
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
        self.base_url = base_url'''

new_init = '''    def __init__(self, api_key: str = None, model: str = None, base_url: str = None, max_tokens: int = None, timeout: float = None):
        """
        初始化 OpenAI 提供者
        
        Args:
            api_key: OpenAI API 密钥（默认使用 API_KEY_POOL[0]）
            model: 模型名称（默认：qwen/qwen3.5-397b-a17b）
            base_url: 自定义 base_url（如 NVIDIA API）
            max_tokens: 最大输出 tokens（GLM4.7 建议 4000-8000，Qwen3.5 建议 16384）
            timeout: 超时时间（秒，默认 180 秒）
        """
        # 如果未指定 api_key，使用 API_KEY_POOL[0]
        if api_key is None:
            api_key = self.API_KEY_POOL[0]
        
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self.base_url = base_url
        self.api_key_index = self.API_KEY_POOL.index(api_key) if api_key in self.API_KEY_POOL else 0'''

content = content.replace(old_init, new_init)

with open('v2_learning_system_real/llm/openai.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ __init__ 修复完成！")
print("   - api_key 现在是可选参数")
print("   - 默认使用 API_KEY_POOL[0]")
