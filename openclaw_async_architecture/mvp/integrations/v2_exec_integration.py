"""
V2集成exec自主工具方案
提升质量：自主可控，减少OpenClaw依赖
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
mvp_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(mvp_src))

from tools.exec_self import execute


class V2WorkerWithSelfExec:
    """V2 Worker使用自主exec工具"""

    def __init__(self, name="v2-worker-"):
        self.name = name

    async def execute_script(
        self,
        script_path: str,
        timeout: int = 30,
        background: bool = False
    ):
        """
        执行Python脚本

        Args:
            script_path: 脚本路径
            timeout: 超时时间
            background: 是否后台运行

        Returns:
            (exit_code, stdout, stderr)
        """
        print(f"[V2 Worker {self.name}] 执行脚本: {script_path}")

        exit_code, stdout, stderr = await execute(
            command=f"python {script_path}",
            timeout=timeout,
            background=background
        )

        if exit_code == 0:
            print(f"[V2 Worker {self.name}] ✅ 执行成功")
            return {"status": "success", "output": stdout}
        else:
            print(f"[V2 Worker {self.name}] ❌ 执行失败")
            return {"status": "failed", "error": stderr, "exit_code": exit_code}


# 集成示例
async def example_usage():
    """使用示例"""

    print("\n" + "="*70)
    print("V2 Worker + 自主exec工具 集成示例")
    print("="*70 + "\n")

    worker = V2WorkerWithSelfExec(name="test")

    # 测试执行Python脚本
    result = await worker.execute_script("--version")  # python --version

    print("\n结果:")
    print(f"  状态: {result['status']}")
    if result['status'] == 'success':
        print(f"  输出: {result['output']}")
    else:
        print(f"  错误: {result.get('error', 'Unknown')}")
        print(f"  退出码: {result.get('exit_code')}")

    print("\n" + "="*70)
    print("集成完成！")
    print("="*70 + "\n")

    print("下一步: 集成到V2 Worker")
    print("  1. 替换OpenClaw的exec调用")
    print("  2. 使用自主execute函数")
    print("  3. 提升自主可控性 🟡")
    print()


if __name__ == "__main__":
    asyncio.run(example_usage())
