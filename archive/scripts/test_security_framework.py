# -*- coding: utf-8 -*-
"""测试安全框架"""

import sys
import os
import asyncio

# 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 切换目录
mvp_dir = os.path.join(os.path.dirname(__file__), 'openclaw_async_architecture', 'mvp')
os.chdir(mvp_dir)
sys.path.insert(0, mvp_dir)

from src.worker.tools.security import (
    validate_path,
    validate_command,
    validate_python_code,
    with_timeout,
    mask_sensitive_data,
)

print("="*70)
print("安全框架测试")
print("="*70)

# 测试1：路径白名单 - 正常路径
print("\n[测试1] 路径白名单 - 正常路径")
try:
    path = validate_path(r"C:\Users\10952\.openclaw\workspace\test.txt")
    print(f"  [OK] 路径验证通过: {path}")
except Exception as e:
    print(f"  [X] 验证失败: {e}")

# 测试2：路径白名单 - 路径遍历攻击
print("\n[测试2] 路径白名单 - 路径遍历攻击")
try:
    path = validate_path(r"C:\Users\10952\.openclaw\workspace\..\..\..\Windows\System32\config\SAM")
    print(f"  [X] 路径验证通过（应该失败）: {path}")
except ValueError as e:
    print(f"  [OK] 检测到攻击: {e}")
except Exception as e:
    print(f"  [X] 其他错误: {e}")

# 测试3：路径白名单 - 不在白名单中的路径
print("\n[测试3] 路径白名单 - 不在白名单中的路径")
try:
    path = validate_path(r"C:\Windows\System32\config\SAM")
    print(f"  [X] 路径验证通过（应该失败）: {path}")
except PermissionError as e:
    print(f"  [OK] 路径被拒绝: {e}")
except Exception as e:
    print(f"  [X] 其他错误: {e}")

# 测试4：命令白名单 - 正常命令
print("\n[测试4] 命令白名单 - 正常命令")
try:
    validate_command("ls -la")
    print(f"  [OK] 命令验证通过")
except Exception as e:
    print(f"  [X] 验证失败: {e}")

# 测试5：命令白名单 - 危险命令
print("\n[测试5] 命令白名单 - 危险命令")
try:
    validate_command("rm -rf /")
    print(f"  [X] 命令验证通过（应该失败）")
except ValueError as e:
    print(f"  [OK] 检测到危险命令: {e}")
except Exception as e:
    print(f"  [X] 其他错误: {e}")

# 测试6：命令白名单 - 不在白名单中的命令
print("\n[测试6] 命令白名单 - 不在白名单中的命令")
try:
    validate_command("chmod +x file.sh")
    print(f"  [X] 命令验证通过（应该失败）")
except PermissionError as e:
    print(f"  [OK] 命令被拒绝: {e}")
except Exception as e:
    print(f"  [X] 其他错误: {e}")

# 测试7：Python代码限制 - 正常代码
print("\n[测试7] Python代码限制 - 正常代码")
try:
    validate_python_code("result = 1 + 1\nprint(result)")
    print(f"  [OK] 代码验证通过")
except Exception as e:
    print(f"  [X] 验证失败: {e}")

# 测试8：Python代码限制 - 危险函数
print("\n[测试8] Python代码限制 - 危险函数")
try:
    validate_python_code("with open('file.txt') as f: print(f.read())")
    print(f"  [X] 代码验证通过（应该失败）")
except ValueError as e:
    print(f"  [OK] 检测到危险函数: {e}")
except Exception as e:
    print(f"  [X] 其他错误: {e}")

# 测试9：敏感数据掩码
print("\n[测试9] 敏感数据掩码")
data = {
    "username": "test",
    "password": "secret123",
    "api_key": "sk-123456",
    "content": "normal data"
}
masked = mask_sensitive_data(data)
print(f"  原始数据: {data}")
print(f"  掩码数据: {masked}")
if masked["password"] == "***HIDDEN***" and masked["api_key"] == "***HIDDEN***":
    print(f"  [OK] 敏感数据已掩码")
else:
    print(f"  [X] 掩码失败")

# 测试10：超时限制
print("\n[测试10] 超时限制")
@with_timeout(timeout_seconds=1.0)
async def slow_function():
    import asyncio
    await asyncio.sleep(2.0)
    return "done"

async def test10():
    try:
        result = await slow_function()
        print(f"  [X] 函数执行完成（应该超时）: {result}")
    except TimeoutError as e:
        print(f"  [OK] 超时捕获: {e}")
    except Exception as e:
        print(f"  [X] 其他错误: {e}")

asyncio.run(test10())

# 测试11：正常超时函数
print("\n[测试11] 正常超时函数（快速）")
@with_timeout(timeout_seconds=3.0)
async def fast_function():
    import asyncio
    await asyncio.sleep(0.5)
    return "done"

async def test11():
    try:
        result = await fast_function()
        print(f"  [OK] 函数执行完成: {result}")
    except Exception as e:
        print(f"  [X] 错误: {e}")

asyncio.run(test11())

print("\n[完成] 所有测试完成")
print("="*70)
