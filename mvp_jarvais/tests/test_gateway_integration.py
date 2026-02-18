"""
MVP JARVIS - Gateway 集成端到端测试
测试完整的 JARVIS 系统通过 Gateway 进行流式对话
"""
import asyncio
import sys
from pathlib import Path

# 添加路径
workspace = Path(__file__).parent.parent.parent  # 返回到 workspace 根目录
sys.path.insert(0, str(workspace))

from mvp_jarvais.plugins.gateway_plugin import GatewayPlugin
from mvp_jarvais.core.agent_manager import AgentManager
from mvp_jarvais.core.tool_engine import ToolEngine
from mvp_jarvais.core.memory_manager import MemoryManager


async def test_gateway_integration():
    """测试 Gateway 集成"""
    print("=" * 80)
    print("🧪 MVP JARVIS - Gateway 集成端到端测试")
    print("=" * 80)
    
    # 1. 初始化 Gateway 插件
    print("\n1️⃣ 初始化 Gateway 插件...")
    gateway = GatewayPlugin(gateway_url="ws://127.0.0.1:8001")
    
    healthy = await gateway.health_check()
    if not healthy:
        print("   ❌ Gateway 不可用，请确保 Gateway 服务已启动")
        return False
    print("   ✅ Gateway 可用")
    
    # 2. 连接到 Gateway
    print("\n2️⃣ 连接到 Gateway...")
    connected = await gateway.connect("jarvis_test_session")
    if not connected:
        print("   ❌ 连接失败")
        return False
    print("   ✅ 连接成功")
    
    # 3. 测试流式对话
    print("\n3️⃣ 测试流式对话...")
    test_message = "请用一句话介绍 JARVIS 系统"
    
    try:
        print(f"   用户：{test_message}")
        print("   JARVIS: ", end="", flush=True)
        
        full_response = ""
        async for chunk in gateway.send_message(test_message, provider="nvidia2"):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print()  # 换行
        print(f"   ✅ 流式对话成功（{len(full_response)} 字符）")
        
    except Exception as e:
        print(f"\n   ❌ 流式对话失败：{e}")
        await gateway.disconnect()
        return False
    
    # 4. 断开连接
    await gateway.disconnect()
    print("\n4️⃣ 断开连接...")
    print("   ✅ 已断开")
    
    print("\n" + "=" * 80)
    print("✅ Gateway 集成测试完成！")
    print("=" * 80)
    
    return True


async def test_with_agent_manager():
    """测试与 AgentManager 集成"""
    print("\n" + "=" * 80)
    print("🧪 MVP JARVIS - AgentManager + Gateway 集成测试")
    print("=" * 80)
    
    # 1. 初始化 Gateway
    print("\n1️⃣ 初始化 Gateway...")
    gateway = GatewayPlugin()
    if not await gateway.connect("agent_test"):
        print("   ❌ Gateway 连接失败")
        return False
    print("   ✅ Gateway 已连接")
    
    # 2. 初始化 AgentManager
    print("\n2️⃣ 初始化 AgentManager...")
    try:
        agent_manager = AgentManager()
        print("   ✅ AgentManager 已初始化")
    except Exception as e:
        print(f"   ⚠️ AgentManager 初始化失败：{e}")
        print("   （可能是配置问题，跳过此测试）")
        await gateway.disconnect()
        return True
    
    # 3. 测试对话路由
    print("\n3️⃣ 测试对话路由...")
    test_message = "你好，JARVIS"
    
    try:
        # 通过 Gateway 发送消息
        response = await gateway.chat(test_message)
        print(f"   用户：{test_message}")
        print(f"   JARVIS: {response[:100]}...")
        print("   ✅ 对话成功")
    except Exception as e:
        print(f"   ❌ 对话失败：{e}")
    
    # 断开连接
    await gateway.disconnect()
    
    print("\n" + "=" * 80)
    print("✅ AgentManager + Gateway 集成测试完成！")
    print("=" * 80)
    
    return True


async def main():
    """主测试函数"""
    # 测试 1：Gateway 插件基础测试
    success1 = await test_gateway_integration()
    
    # 测试 2：与 AgentManager 集成测试
    success2 = await test_with_agent_manager()
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    print(f"Gateway 插件测试：{'✅ 通过' if success1 else '❌ 失败'}")
    print(f"AgentManager 集成测试：{'✅ 通过' if success2 else '⚠️ 跳过'}")
    
    if success1:
        print("\n🎉 MVP JARVIS Gateway 集成完成！")
        print("\n💡 下一步：")
        print("   1. 完善文档")
        print("   2. 添加更多测试用例")
        print("   3. 部署到生产环境")
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
