"""测试V1 Gateway API调用"""
import requests
import json

V1_GATEWAY = "http://127.0.0.1:18790"
TOKEN = "lbprg74nqGxsvopWqkgLAAefoIWKobzH"

def test_v1_api():
    """测试V1 Gateway API"""
    print("="*50)
    print("测试 V1 Gateway API")
    print("="*50)

    url = f"{V1_GATEWAY}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "cherry-nvidia/z-ai/glm4.7",
        "messages": [{"role": "user", "content": "你好，请用一句话介绍你自己"}],
        "max_tokens": 100
    }

    print(f"\n📡 请求: {url}")
    print(f"📝 提示: {payload['messages'][0]['content']}")

    try:
        import time
        start_time = time.time()

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        end_time = time.time()
        latency = end_time - start_time

        print(f"\n⏱️  响应时间: {latency:.2f}秒")
        print(f"📊 状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            tokens = result.get('usage', {}).get('total_tokens', 'N/A')

            print(f"\n✅ 调用成功")
            print(f"📦 返回内容: {content}")
            print(f"🪙 Token使用: {tokens}")

            return True
        else:
            print(f"\n❌ 调用失败")
            print(f"错误信息: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"\n❌ 请求超时（>30秒）")
        return False
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False


if __name__ == "__main__":
    success = test_v1_api()

    print("\n" + "="*50)
    if success:
        print("✅ V1 Gateway API 可用，可以启动MVP")
    else:
        print("❌ V1 Gateway API 不可用，请检查Gateway配置")
    print("="*50)
