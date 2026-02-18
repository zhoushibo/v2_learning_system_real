"""详细错误诊断测试"""
import asyncio
import time
from v2_learning_system_real.llm.openai import OpenAIProvider

async def test_with_details():
    print("=" * 80)
    print("🔍 详细错误诊断")
    print("=" * 80)
    
    provider = OpenAIProvider()
    print(f"\n✅ 初始化成功")
    print(f"   模型：{provider.model}")
    print(f"   API Key: {provider.API_KEY_POOL[0][:10]}...{provider.API_KEY_POOL[0][-5:]}")
    print(f"   Base URL: {provider.base_url}")
    
    print("\n📞 尝试真实 API 调用...")
    start_time = time.time()
    
    try:
        # 直接调用 learning 方法，绕过 fallback
        result = await provider.learning(
            topic="Python 是什么？",
            perspective="简单定义",
            style="简洁"
        )
        end_time = time.time()
        print(f"✅ API 调用成功！耗时：{end_time - start_time:.2f}秒")
        print(f"   结果：{result}")
        
    except Exception as e:
        end_time = time.time()
        print(f"❌ API 调用失败！耗时：{end_time - start_time:.2f}秒")
        print(f"   错误类型：{type(e).__name__}")
        print(f"   错误信息：{e}")
        
        # 打印完整堆栈
        import traceback
        print("\n📋 完整堆栈跟踪:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_with_details())
