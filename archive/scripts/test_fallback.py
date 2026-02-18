"""
测试多模型自动 fallback 功能

测试场景：
1. 主模型成功
2. 主模型失败 → 自动切换到备用模型
3. 所有模型失败 → 抛出错误
"""

import asyncio
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# 直接导入，避免循环依赖
import sys
sys.path.insert(0, 'v2_learning_system_real')
from llm.openai import OpenAIProvider

# 简单配置
class SimpleConfig:
    nvidia_api_key = os.getenv('NVIDIA_API_KEY')
    
config = SimpleConfig()

async def test_fallback():
    """测试自动 fallback 功能"""
    
    print("=" * 60)
    print("🧪 测试多模型自动 fallback")
    print("=" * 60)
    
    # 初始化提供者
    api_key = os.getenv('NVIDIA_API_KEY')
    if not api_key:
        print("❌ 错误：未设置 NVIDIA_API_KEY 环境变量")
        print("请设置：$env:NVIDIA_API_KEY='your_key'")
        return False
        
    provider = OpenAIProvider(
        api_key=api_key,
        base_url="https://integrate.api.nvidia.com/v1",
        model="qwen/qwen3.5-397b-a17b"
    )
    
    # 测试主题
    topic = "Python 异步编程"
    perspective = "Python 专家"
    
    print(f"\n📚 学习主题：{topic}")
    print(f"🎯 视角：{perspective}")
    print(f"🔄 使用 learning_with_fallback() 自动切换")
    print("-" * 60)
    
    try:
        # 调用带 fallback 的学习
        result = await provider.learning_with_fallback(
            topic=topic,
            perspective=perspective,
            style="deep_analysis",
            max_retries=2
        )
        
        print("\n✅ 学习成功！")
        print("\n📋 学习结果:")
        print(f"  课程数：{len(result.get('lessons', []))}")
        print(f"  要点数：{len(result.get('key_points', []))}")
        print(f"  建议数：{len(result.get('recommendations', []))}")
        
        print("\n📖 课程列表:")
        for i, lesson in enumerate(result.get('lessons', [])[:3], 1):
            print(f"  {i}. {lesson}")
        
        print("\n💡 关键要点:")
        for i, point in enumerate(result.get('key_points', [])[:3], 1):
            print(f"  {i}. {point}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 学习失败：{e}")
        print("\n可能原因:")
        print("  1. API Key 无效")
        print("  2. 所有模型都暂时不可用")
        print("  3. 网络连接问题")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fallback())
    sys.exit(0 if success else 1)
