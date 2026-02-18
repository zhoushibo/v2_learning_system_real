"""更新 CLI 的 route_learn 方法"""
from pathlib import Path

cli_file = Path('v2_cli/cli.py')
with open(cli_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找并替换
old_start = "    async def route_learn(self, args: str):"
old_end = "    async def route_exec(self, args: str):"

start_idx = content.find(old_start)
end_idx = content.find(old_end)

if start_idx == -1 or end_idx == -1:
    print("❌ 未找到 route_learn 或 route_exec 方法")
    exit(1)

# 新的 route_learn 方法
new_route_learn = '''    async def route_learn(self, args: str):
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
        
        console.print(f"\\n[bold cyan]📚 开始学习：{topic}[/bold cyan]")
        console.print(f"[dim]Workers: {workers}, Perspectives: {perspectives}[/dim]\\n")
        
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
            
            console.print(f"\\n[bold green]✅ 学习完成！耗时：{duration:.2f}秒[/bold green]\\n")
            
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
                    console.print(f"  {content}\\n")
            
            console.print(f"[dim]💡 提示：使用 -w 和 -p 选项调整 Worker 数量和视角数量[/dim]")
            
        except ImportError as e:
            console.print(f"[red]错误：V2 学习系统未找到 - {e}[/red]")
        except Exception as e:
            console.print(f"[red]错误：{e}[/red]")

'''

# 替换
new_content = content[:start_idx] + new_route_learn + content[end_idx:]

with open(cli_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ route_learn 方法已更新！")
print(f"   位置：行 {content[:start_idx].count(chr(10))+1} 到 {content[:end_idx].count(chr(10))+1}")
