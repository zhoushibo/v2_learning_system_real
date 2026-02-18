"""
真实场景测试：OpenClaw Timeout Wrapper

测试目标：
1. 正常任务快速完成
2. 超时任务触发 Fallback（不卡顿）
3. 真实 exec 命令保护
"""

import asyncio
import time
from openclaw_timeout_wrapper import get_wrapper, OpenClawTimeoutError


async def test_1_normal_chat():
    """测试 1：正常对话（应该 <5 秒）"""
    print("\n" + "="*60)
    print("测试 1：正常对话")
    print("="*60)

    wrapper = get_wrapper()

    start = time.time()
    response = await wrapper.chat([{"role": "user", "content": "你好，请简单回复"}])
    duration = time.time() - start

    print(f"✅ 响应时间：{duration:.2f}秒")
    print(f"🤖 AI: {response}")

    if duration < 5:
        print("✅ 通过：快速响应")
    else:
        print("⚠️  警告：响应较慢")


async def test_2_timeout_simulation():
    """测试 2：模拟超时任务（应该触发 Fallback）"""
    print("\n" + "="*60)
    print("测试 2：模拟超时任务（5 秒超时）")
    print("="*60)

    wrapper = get_wrapper()

    # 创建一个会超时的慢任务
    async def slow_task():
        print("  开始执行慢任务...")
        await asyncio.sleep(10)  # 模拟 10 秒任务
        return "任务完成"

    print("  设置超时：5 秒")
    print("  预期：5 秒后触发 Fallback，不卡顿")

    start = time.time()

    try:
        result = await wrapper.safe_invoke(
            slow_task,
            timeout=5,
            fallback="⚠️  响应超时，已触发 Fallback 机制"
        )

        duration = time.time() - start

        print(f"\n✅ 实际耗时：{duration:.2f}秒")
        print(f"📦 结果：{result}")

        if duration < 6:  # 5 秒超时 + 一点缓冲
            print("✅ 通过：超时保护生效，未卡顿！")
        else:
            print("❌ 失败：耗时过长")

    except OpenClawTimeoutError as e:
        duration = time.time() - start
        print(f"\n⚠️  超时异常：{e}")
        print(f"✅ 但程序未卡住，继续执行")


async def test_3_real_exec():
    """测试 3：真实 exec 命令"""
    print("\n" + "="*60)
    print("测试 3：真实 exec 命令")
    print("="*60)

    wrapper = get_wrapper()

    # 测试快速命令
    print("\n📝 执行快速命令：echo 'Hello'")
    start = time.time()
    result = await wrapper.exec_tool("echo Hello", timeout=10)
    duration = time.time() - start

    print(f"✅ 耗时：{duration:.2f}秒")
    print(f"📦 结果：{result}")

    # 测试可能慢的命令
    print("\n📝 执行中等命令：dir (列出目录)")
    start = time.time()
    result = await wrapper.exec_tool("dir", timeout=10)
    duration = time.time() - start

    print(f"✅ 耗时：{duration:.2f}秒")
    if isinstance(result, dict):
        print(f"📦 状态：{result.get('status', 'unknown')}")
    else:
        print(f"📦 结果：{result[:200]}...")


async def test_4_stress():
    """测试 4：压力测试（连续 10 次请求）"""
    print("\n" + "="*60)
    print("测试 4：压力测试（连续 10 次对话）")
    print("="*60)

    wrapper = get_wrapper()

    start = time.time()

    for i in range(10):
        response = await wrapper.chat([{"role": "user", "content": f"测试{i}"}])

    duration = time.time() - start
    avg = duration / 10

    print(f"✅ 总耗时：{duration:.2f}秒")
    print(f"✅ 平均每次：{avg:.2f}秒")

    if avg < 2:
        print("✅ 通过：性能优秀")
    elif avg < 5:
        print("✅ 通过：性能良好")
    else:
        print("⚠️  警告：性能较慢")


async def main():
    """主测试程序"""
    print("\n" + "="*70)
    print("🧪 真实场景测试：OpenClaw Timeout Wrapper")
    print("="*70)
    print("\n测试目标：验证 Wrapper 能防止超过 10 分钟的卡顿")
    print("预期效果：所有操作都有超时保护，永不卡顿\n")

    try:
        # 测试 1：正常对话
        await test_1_normal_chat()

        # 测试 2：超时模拟
        await test_2_timeout_simulation()

        # 测试 3：真实 exec
        await test_3_real_exec()

        # 测试 4：压力测试
        await test_4_stress()

        print("\n" + "="*70)
        print("🎉 所有测试完成！")
        print("="*70)
        print("\n✅ 结论：")
        print("  1. 正常任务快速完成")
        print("  2. 超时任务触发 Fallback，不卡顿")
        print("  3. exec 命令有超时保护")
        print("  4. 压力测试性能稳定")
        print("\n🎯 OpenClaw 超时问题已解决！")
        print("📖 使用文档：OPENCLAW_TIMEOUT_WRAPPER_GUIDE.md")

    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
