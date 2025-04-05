#!/usr/bin/env python
"""
智能中文网络小说生成系统主程序入口
"""

import asyncio
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

try:
    import config
except ImportError:
    print("错误: 找不到配置文件。请复制 config.example.py 到 config.py 并配置您的API密钥。")
    sys.exit(1)

from novel_generator.agents.world_builder import WorldBuilderAgent
from novel_generator.storage.json_storage import JsonStorage
from novel_generator.models.world import World


console = Console()


async def create_world(storage: JsonStorage):
    """创建新的世界观设定"""
    console.print(Panel.fit("创建新的世界观", title="世界观构建", border_style="green"))
    
    description = Prompt.ask("\n请描述您想要的世界观\n(例如：一个融合了东方玄幻和西方奇幻元素的世界，有独特的灵气修炼体系...)\n")
    
    if not description:
        console.print("[yellow]描述为空，已取消创建[/yellow]")
        return
    
    console.print("[bold green]正在生成世界观，这可能需要一些时间...[/bold green]")
    
    try:
        agent = WorldBuilderAgent(api_key=config.GEMINI_API_KEY, 
                                  temperature=config.TEMPERATURE, 
                                  top_p=config.TOP_P)
        
        world = await agent.create_world(description)
        
        # 保存世界观
        storage.save(world.to_dict(), "worlds", world.id)
        
        # 打印世界观摘要
        console.print(Panel(world.get_summary(), 
                            title=f"世界观：{world.name}", 
                            border_style="green",
                            expand=False))
        
        console.print(f"[green]世界观已保存! ID: {world.id}[/green]")
        
        return world
    
    except Exception as e:
        console.print(f"[bold red]创建世界观时出错: {e}[/bold red]")
        return None


async def list_worlds(storage: JsonStorage):
    """列出所有已创建的世界观"""
    worlds = storage.list("worlds")
    
    if not worlds:
        console.print("[yellow]还没有创建任何世界观[/yellow]")
        return None
    
    console.print(Panel.fit("已创建的世界观", title="世界列表", border_style="blue"))
    
    for i, world in enumerate(worlds, 1):
        console.print(f"[blue]{i}.[/blue] {world['name']} (ID: {world['id']})")
    
    index = Prompt.ask("请选择一个世界观（输入序号）", default="1")
    try:
        index = int(index) - 1
        if 0 <= index < len(worlds):
            world_data = storage.load("worlds", worlds[index]["id"])
            world = World.from_dict(world_data)
            
            # 打印世界观摘要
            console.print(Panel(world.get_summary(), 
                                title=f"世界观：{world.name}", 
                                border_style="green",
                                expand=False))
            
            return world
        else:
            console.print("[yellow]无效的选择[/yellow]")
            return None
    except ValueError:
        console.print("[yellow]请输入有效的数字[/yellow]")
        return None


async def main_menu():
    """主菜单"""
    storage = JsonStorage(base_dir=config.DATA_DIR)
    
    console.print(Panel.fit(
        "欢迎使用智能中文网络小说生成系统 v0.1.0",
        title="◈ 网文生成器 ◈",
        border_style="blue"
    ))
    
    current_world = None
    
    while True:
        console.print("\n[bold blue]===== 主菜单 =====[/bold blue]")
        
        if current_world:
            console.print(f"当前世界: [green]{current_world.name}[/green]")
        
        console.print("1. 创建新的世界观")
        console.print("2. 查看已有世界观")
        console.print("3. 创建角色 (即将推出)")
        console.print("4. 设计剧情 (即将推出)")
        console.print("5. 生成小说 (即将推出)")
        console.print("0. 退出")
        
        choice = Prompt.ask("请选择", choices=["0", "1", "2", "3", "4", "5"], default="1")
        
        if choice == "0":
            if Confirm.ask("确定要退出吗?"):
                break
        
        elif choice == "1":
            current_world = await create_world(storage)
        
        elif choice == "2":
            current_world = await list_worlds(storage)
        
        else:
            console.print("[yellow]该功能尚未实现，敬请期待![/yellow]")


if __name__ == "__main__":
    # 确保数据目录存在
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        console.print("\n[bold red]程序已中断[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]发生错误: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
    
    console.print("[bold blue]感谢使用，再见！[/bold blue]") 