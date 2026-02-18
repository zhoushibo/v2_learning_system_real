"""
测试NVIDIA API响应格式
"""
import asyncio
from openai import AsyncOpenAI

async def test_nvidia_api():
    """测试NVIDIA API"""
    print("测试NVIDIA API响应格式...\n")

    # 从配置读取
    import json
    with open("C:/Users/10952/.openclaw/openclaw.cherry.json", 'r', encoding='utf-8') as f:
        config = json.load(f)

    provider_config = config["models"]["providers"]["cherry-nvidia"]
    api_key = provider_config["apiKey"]
    base_url = provider_config["baseUrl"]

    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:20]}...\n")

    # 创建客户端
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url
    )

    # 发送请求
    print("发送请求...")
    response = await client.chat.completions.create(
        model="z-ai/glm4.7",
        messages=[
            {
                "role": "user",
                "content": "你好，请用JSON格式回复，包含'hello'和'world'两个字段。"
            }
        ],
        temperature=0.7,
        max_tokens=100
    )

    print(f"\n响应类型: {type(response)}")
    print(f"响应: {response}")

    # 检查结构
    if hasattr(response, 'choices'):
        print(f"\nchoices存在: {response.choices}")
        if response.choices:
            print(f"第一个choice: {response.choices[0]}")
            if hasattr(response.choices[0], 'message'):
                print(f"message: {response.choices[0].message}")
                if hasattr(response.choices[0].message, 'content'):
                    print(f"\ncontent: {response.choices[0].message.content}")
            else:
                print("无message字段")
        else:
            print("choices为空")
    else:
        print("无choices字段")

    # 打印所有属性
    print(f"\n所有属性: {dir(response)}")

if __name__ == "__main__":
    asyncio.run(test_nvidia_api())
