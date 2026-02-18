"""
Gateway流式对话 - 立即可用
提升效率：流式体验，边生边出
"""

import asyncio
import websockets
import json
import sys

# Windows编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

class StreamingChat:
    """流式对话客户端"""

    def __init__(self, gateway_url="ws://127.0.0.1:8001"):
        self.gateway_url = gateway_url

    async def chat(
        self,
        message: str,
        provider: str = "nvidia2",
        session_id: str = "default-session"
    ):
        """
        流式对话

        Args:
            message: 用户消息
            provider: API提供商 (nvidia2/hunyuan/zhipu)
            session_id: 会话ID
        """
        uri = f"{self.gateway_url}/ws/stream/{session_id}"

        async with websockets.connect(uri) as websocket:
            # 发送消息
            payload = {
                "message": message,
                "provider": provider
            }
            await websocket.send(json.dumps(payload, ensure_ascii=False))

            # 接收流式响应
            full_response = ""

            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)

                    # 尝试解析为JSON
                    try:
                        data = json.loads(response)

                        if data.get("type") == "done":
                            print("\n\n[✅ 完成]")
                            break
                        elif data.get("type") == "error":
                            print(f"\n\n[❌ 错误]: {data.get('message')}")
                            break
                    except json.JSONDecodeError:
                        # 普通文本，直接输出
                        full_response += response
                        print(response, end="", flush=True)

                except asyncio.TimeoutError:
                    print("\n\n[❌ 超时]")
                    break
                except Exception as e:
                    print(f"\n\n[❌ 错误]: {e}")
                    break

            return full_response


# 便捷函数
async def chat(message: str, provider: str = "nvidia2"):
    """
    快速流式对话

    Args:
        message: 用户消息
        provider: API提供商（推荐hunyuan，更快）

    Returns:
        完整响应文本
    """
    client = StreamingChat()
    return await client.chat(message, provider=provider)


# 交互式命令行
async def interactive_chat():
    """交互式对话"""
    client = StreamingChat()

    print("\n" + "="*70)
    print("Gateway流式对话 - 立即可用")
    print("="*70 + "\n")

    print("可用API:")
    print("  - nvidia2（默认，较快）")
    print("  - hunyuan（最快，661ms首字）⭐ 推荐")
    print("  - zhipu（速度最快，但有限流）")
    print()

    session_id = "interactive-session"

    while True:
        print("-" * 70)
        try:
            message = input("\n👤 你: ").strip()

            if not message:
                continue

            if message.lower() in ["exit", "quit", "退出"]:
                print("\n👋 再见！")
                break

            # 选择API
            provider = input("📌 API [nvidia2/hunyuan/zhipu]: ").strip() or "hunyuan"
            if provider not in ["nvidia2", "hunyuan", "zhipu"]:
                provider = "hunyuan"

            # 发送和接收
            print(f"\n🤖 AI ({provider}):")
            print("-" * 70)

            await client.chat(message, provider=provider, session_id=session_id)

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")


# 直接使用示例
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--message", help="单次对话消息")
    parser.add_argument("--provider", default="hunyuan", help="API提供商")
    parser.add_argument("--interactive", action="store_true", help="交互模式")

    args = parser.parse_args()

    if args.interactive:
        asyncio.run(interactive_chat())
    elif args.message:
        asyncio.run(chat(args.message, provider=args.provider))
    else:
        print("使用方法:")
        print("  交互模式: python use_gateway.py --interactive")
        print("  单次对话: python use_gateway.py --message '你好' --provider hunyuan")
