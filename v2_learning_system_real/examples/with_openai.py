"""
示例：使用真实OpenAI API进行学习

配置步骤：
1. 安装依赖：pip install openai
2. 创建.env文件
3. 添加：OPENAI_API_KEY=your_api_key_here
"""
import asyncio
import os
from dotenv import load_dotenv

# 导入学习系统
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_engine import V2LearningSystem
from llm import OpenAIProvider


async def main():
    """主程序 - 使用真实OpenAI API"""
    print("="*70)
    print("🎓 V2学习系统示例 - 使用真实OpenAI API")
    print("="*70)

    # 加载环境变量
    load_dotenv()

    # 获取API密钥
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("\n❌ 错误：未找到OPENAI_API_KEY环境变量")
        print("\n请按以下步骤配置：")
        print("1. 创建.env文件")
        print("2. 添加：OPENAI_API_KEY=your_api_key_here")
        print("3. 保存文件")
        return

    # 创建OpenAI提供者
    print(f"\n✅ 环境配置：OPENAI_API_KEY={api_key[:8]}...")

    llm_provider = OpenAIProvider(
        api_key=api_key,
        model="gpt-4"  # 可以换成 "gpt-3.5-turbo" 以降低成本
    )

    # 验证API密钥
    print("\n验证API密钥...")
    is_valid = await llm_provider.validate_key()

    if not is_valid:
        print("\n❌ API密钥验证失败，请检查密钥是否正确")
        return

    print("✅ API密钥验证成功")

    # 创建学习系统
    learning_system = V2LearningSystem(
        num_workers=5,
        llm_provider=llm_provider
    )

    # 启动并行学习
    # 可以更换为任何你想学习的主题
    await learning_system.start_parallel_learning("React Hooks深度学习")

    print("\n💡 提示：")
    print("  - 学习历史已保存")
    print("  - 可以尝试学习其他主题")
    print("  - 系统会积累知识，越用越强")


if __name__ == "__main__":
    asyncio.run(main())
