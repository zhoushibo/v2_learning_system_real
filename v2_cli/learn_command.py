"""
V2 CLI - learn 命令实现
使用 V2 学习系统进行并行学习
"""
import asyncio
import time
import json
import sys
from pathlib import Path
from rich.console import Console

# 添加 workspace 路径
workspace = Path(__file__).parent.parent
sys.path.insert(0, str(workspace))

console = Console()

async def learn_topic(topic: str, workers: int = 3, perspectives: int = 3):
    """
    使用 V2 学习系统学习主题
    
    Args:
        topic: 学习主题
        workers: Worker 数量
        perspectives: 学习视角数量
    """
    console.print(f"\n[bold cyan]📚 开始学习：{topic}[/bold cyan]")
    console.print(f"[dim]Workers: {workers}, Perspectives: {perspectives}[/dim]\n")
    
    try:
        # 导入 V2 学习系统
        from v2_learning_system_real import LearningEngine
        
        # 初始化学习引擎
        engine = LearningEngine(num_workers=workers)
        
        console.print("[dim]正在启动学习 Worker...[/dim]")
        
        # 执行并行学习
        start_time = time.time()
        results = await engine.parallel_learning(topic, num_perspectives=perspectives)
        end_time = time.time()
        duration = end_time - start_time
        
        # 输出结果
        console.print(f"\n[bold green]✅ 学习完成！耗时：{duration:.2f}秒[/bold green]\n")
        
        for i, result in enumerate(results, 1):
            perspective_name = result.get('perspective', f'视角{i}')
            content = result.get('result', '无内容')
            
            # 解析内容（如果是 JSON 格式）
            try:
                content_data = json.loads(content)
                lessons = content_data.get('lessons', [])
                key_points = content_data.get('key_points', [])
                
                console.print(f"[bold cyan]视角 {i}: {perspective_name}[/bold cyan]")
                if lessons:
                    console.print("[dim]课程要点:[/dim]")
                    for lesson in lessons[:3]:  # 只显示前 3 个
                        console.print(f"  • {lesson}")
                if key_points:
                    console.print("[dim]关键点:[/dim]")
                    for point in key_points[:3]:  # 只显示前 3 个
                        console.print(f"  • {point}")
                console.print()
            except:
                # 非 JSON 格式，直接显示
                console.print(f"[bold cyan]视角 {i}: {perspective_name}[/bold cyan]")
                # 截断长文本
                if len(content) > 500:
                    content = content[:500] + "..."
                console.print(f"  {content}\n")
        
        console.print(f"[dim]💡 提示：使用 -w 和 -p 选项调整 Worker 数量和视角数量[/dim]")
        
    except ImportError as e:
        console.print(f"[red]错误：V2 学习系统未找到 - {e}[/red]")
        console.print("[yellow]请确保 v2_learning_system_real 包已正确安装[/yellow]")
    except Exception as e:
        console.print(f"[red]错误：{e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 测试
    topic = "Python 异步编程"
    asyncio.run(learn_topic(topic, workers=3, perspectives=3))
