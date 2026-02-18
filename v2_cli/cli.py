"""
V2 CLI系统 - 主入口

替代OpenClaw的下一代AI助手

核心命令：
- chat: 对话（Gateway流式）
- learn: 学习（V2学习系统）
- exec: 执行（V2 MCP exec工具）
- workflow: 工作流（FusionWorkflow）
- help/status/history: 辅助命令

架构：
CLI界面（prompt_toolkit）→ CommandRouter → V2 MCP/Gateway/V2学习/FusionWorkflow
"""
import asyncio
import sys
import os
import json
from pathlib import Path

# 添加workspace路径
workspace = Path(__file__).parent.parent
sys.path.insert(0, str(workspace))

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing import List, Optional

# 初始化Rich Console
console = Console()


class V2CLI:
    """V2 CLI系统主类"""

    def __init__(self):
        """初始化V2 CLI"""
        self.running = False
        self.history_file = workspace / "v2_cli_history.txt"
        self.commands = ["chat", "learn", "exec", "workflow", "help", "status", "history", "exit"]

        # 创建命令补全器
        self.completer = WordCompleter(self.commands, ignore_case=True)

        # 创建提示会话
        self.session = PromptSession(
            history=FileHistory(str(self.history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer
        )

        # 初始化各系统（懒加载）
        self._gateway_client = None
        self._worker_pool = None
        self._executor = None
        self._learning_engine = None
        self._workflow_engine = None

        # 加载配置
        self._load_config()

    def _load_config(self):
        """加载配置"""
        config_file = workspace.parent / ".openclaw" / "openclaw.cherry.json"

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

            # 提取NVIDIA配置
            provider_config = self.config["models"]["providers"]["cherry-nvidia"]
            self.nvidia_api_key = provider_config["apiKey"]
            self.nvidia_base_url = provider_config["baseUrl"]
            self.nvidia_model = "z-ai/glm4.7"
        else:
            console.print("[yellow]警告：未找到配置文件[/yellow]")
            self.nvidia_api_key = None
            self.nvidia_base_url = None
            self.nvidia_model = None

    def _load_gateway_client(self):
        """加载Gateway客户端"""
        try:
            # 尝试导入Gateway
            gateway_path = workspace / "openclaw_async_architecture" / "streaming-service"
            sys.path.insert(0, str(gateway_path))

            from use_gateway import StreamingChat

            self._gateway_client = StreamingChat(
                gateway_url="ws://127.0.0.1:8001"
            )
        except ImportError as e:
            console.print(f"[yellow]Gateway未运行：{e}[/yellow]")
            self._gateway_client = None

    @property
    def gateway_client(self):
        """获取Gateway客户端（懒加载）"""
        if self._gateway_client is None:
            self._load_gateway_client()
        return self._gateway_client

    async def run(self):
        """运行V2 CLI"""
        self.running = True

        # 自动确保Gateway服务在运行
        from gateway_manager import ensure_gateway
        await ensure_gateway()
        print()

        # 欢迎信息
        self.print_welcome()

        # 主循环
        while self.running:
            try:
                # 读取用户输入
                user_input = await self.session.prompt_async(
                    "v2> ",
                    style=None,
                    complete_while_typing=True
                )

                # 解析命令
                if not user_input.strip():
                    continue

                # 解析命令和参数
                parts = user_input.strip().split(None, 1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                # 执行命令
                await self.route_command(command, args)

            except KeyboardInterrupt:
                console.print("\n[yellow]Ctrl+C，输入'exit'退出[/yellow]")
            except EOFError:
                console.print("\n再见！")
                break
            except Exception as e:
                console.print(f"[red]错误：{e}[/red]")

    async def route_command(self, command: str, args: str):
        """路由命令到对应的处理器"""
        command_map = {
            "chat": self.route_chat,
            "learn": self.route_learn,
            "exec": self.route_exec,
            "workflow": self.route_workflow,
            "help": self.route_help,
            "status": self.route_status,
            "history": self.route_history,
            "exit": self.route_exit,
            "quit": self.route_exit,
        }

        if command in command_map:
            await command_map[command](args)
        else:
            console.print(f"[red]未知的命令：{command}[/red]")
            console.print("输入 'help' 查看可用命令")

    async def route_chat(self, args: str):
        """处理chat命令（Gateway流式对话）"""
        if not args:
            console.print("[yellow]用法：chat <消息>[/yellow]")
            return

        message = args.strip()
        console.print(f"\n[green]你：{message}[/green]")
        console.print("[blue]V2：[/blue]", end="")

        try:
            client = self.gateway_client
            if client is None:
                console.print("[red]Gateway客户端未初始化[/red]")
                return

            # 流式输出（chat方法会自动打印到stdout）
            console.print()
            full_response = await client.chat(message)

            console.print()  # 换行
        except Exception as e:
            console.print(f"\n[red]错误：{e}[/red]")

    async def route_learn(self, args: str):
        """处理 learn 命令（V2 学习系统）"""
        if not args:
            console.print("[yellow]用法：learn <主题> [-w workers] [-p perspectives][/yellow]")
            return
        
        # 解析参数
        parts = args.split()
        topic_parts = []
        workers = 3
        perspectives = 3
        
        i = 0
        while i < len(parts):
            if parts[i] in ['-w', '--workers'] and i + 1 < len(parts):
                workers = int(parts[i + 1])
                i += 2
            elif parts[i] in ['-p', '--perspectives'] and i + 1 < len(parts):
                perspectives = int(parts[i + 1])
                i += 2
            else:
                topic_parts.append(parts[i])
                i += 1
        
        topic = ' '.join(topic_parts)
        if not topic:
            console.print("[yellow]用法：learn <主题> [-w workers] [-p perspectives][/yellow]")
            return
        
        console.print(f"\n[bold cyan]📚 开始学习：{topic}[/bold cyan]")
        console.print(f"[dim]Workers: {workers}, Perspectives: {perspectives}[/dim]\n")
        
        try:
            from v2_learning_system_real import LearningEngine
            import time
            import json
            
            engine = LearningEngine(num_workers=workers)
            console.print("[dim]正在启动学习 Worker...[/dim]")
            
            start_time = time.time()
            results = await engine.parallel_learning(topic, num_perspectives=perspectives)
            end_time = time.time()
            duration = end_time - start_time
            
            console.print(f"\n[bold green]✅ 学习完成！耗时：{duration:.2f}秒[/bold green]\n")
            
            for i, result in enumerate(results, 1):
                perspective_name = result.get('perspective', f'视角{i}')
                content = result.get('result', '无内容')
                
                try:
                    content_data = json.loads(content)
                    lessons = content_data.get('lessons', [])
                    key_points = content_data.get('key_points', [])
                    
                    console.print(f"[bold cyan]视角 {i}: {perspective_name}[/bold cyan]")
                    if lessons:
                        console.print("[dim]课程要点:[/dim]")
                        for lesson in lessons[:3]:
                            console.print(f"  • {lesson}")
                    if key_points:
                        console.print("[dim]关键点:[/dim]")
                        for point in key_points[:3]:
                            console.print(f"  • {point}")
                    console.print()
                except:
                    console.print(f"[bold cyan]视角 {i}: {perspective_name}[/bold cyan]")
                    if len(content) > 500:
                        content = content[:500] + "..."
                    console.print(f"  {content}\n")
            
            console.print(f"[dim]💡 提示：使用 -w 和 -p 选项调整 Worker 数量和视角数量[/dim]")
            
        except ImportError as e:
            console.print(f"[red]错误：V2 学习系统未找到 - {e}[/red]")
        except Exception as e:
            console.print(f"[red]错误：{e}[/red]")

    async def route_exec(self, args: str):
        """处理exec命令（V2 MCP exec工具）"""
        if not args:
            console.print("[yellow]用法：exec <命令>[/yellow]")
            return

        command = args.strip()
        console.print(f"\n[cyan]执行命令：{command}[/cyan]\n")

        try:
            # TODO: 集成V2 MCP exec工具
            console.print("[yellow]exec工具集成中...[/yellow]")
            console.print("暂未实现，请稍后")
        except Exception as e:
            console.print(f"[red]错误：{e}[/red]")

    async def route_workflow(self, args: str):
        """处理workflow命令（FusionWorkflow）"""
        if not args:
            console.print("[yellow]用法：workflow <工作流名称>[/yellow]")
            return

        workflow_name = args.strip()
        console.print(f"\n[cyan]运行工作流：{workflow_name}[/cyan]\n")

        try:
            # TODO: 集成FusionWorkflow
            console.print("[yellow]FusionWorkflow集成中...[/yellow]")
            console.print("暂未实现，请稍后")
        except Exception as e:
            console.print(f"[red]错误：{e}[/red]")

    def route_help(self, args: str):
        """处理help命令"""
        help_text = """
[bold]V2 CLI系统 - 命令帮助[/bold]

[underline]核心命令：[/underline]
  chat <消息>        - 流式对话（Gateway）
  learn <主题>       - 学习新知识（V2学习系统）
  exec <命令>        - 执行Shell命令（V2 MCP）
  workflow <名称>    - 运行工作流（FusionWorkflow）

[underline]辅助命令：[/underline]
  help              - 显示此帮助信息
  status            - 显示系统状态
  history           - 显示命令历史
  exit / quit        - 退出V2 CLI

[underline]特性：[/underline]
  - Tab补全命令
  - 上下箭头查看历史
  - Ctrl+C中断当前命令
  - 流式输出（Gateway）
  - 并发执行（Worker Pool）
        """
        console.print(help_text)

    def route_status(self, args: str):
        """处理status命令"""
        status_text = """
[bold]V2 CLI系统 - 系统状态[/bold]

[underline]V2 MCP组件：[/underline]
  - Gateway流式：[green]已集成[/green] ✅
  - Worker Pool：[yellow]待集成[/yellow] ⏳
  - exec工具：[yellow]待集成[/yellow] ⏳

[underline]其他V2系统：[/underline]
  - V2学习系统：[yellow]待集成[/yellow] ⏳
  - FusionWorkflow：[yellow]待集成[/yellow] ⏳

[underline]配置：[/underline]
  - NVIDIA API：[green]已配置[/green] ✅
  - 模型：[cyan]{model}[/cyan]

[underline]历史：[/underline]
  - 历史文件：{history_file}
        """.format(
            model=self.nvidia_model or "未配置",
            history_file=self.history_file
        )
        console.print(status_text)

    def route_history(self, args: str):
        """处理history命令"""
        if not self.history_file.exists():
            console.print("[yellow]无历史记录[/yellow]")
            return

        with open(self.history_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        console.print("\n[bold]命令历史（最近20条）：[/bold]")
        for line in lines[-20:]:
            console.print(f"  {line.strip()}")

    async def route_exit(self, args: str):
        """处理exit命令"""
        console.print("[green]再见！[/green]")
        self.running = False

    def print_welcome(self):
        """打印欢迎信息"""
        welcome_text = """
[bold cyan]==================================================[/bold cyan]
[bold cyan]           V2 CLI System v1.0[/bold cyan]
[bold cyan]       替代OpenClaw的下一代AI助手[/bold cyan]
[bold cyan]==================================================[/bold cyan]

[i]输入 'help' 查看命令，输入 'exit' 退出[/i]
        """
        console.print(welcome_text)


def main():
    """主入口"""
    cli = V2CLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()
