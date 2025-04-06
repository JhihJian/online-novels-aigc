#!/usr/bin/env python
"""
智能中文网络小说生成系统主程序入口
"""

import asyncio
import sys
import os
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

try:
    import config
except ImportError:
    print("错误: 找不到配置文件。请复制 config.example.py 到 config.py 并配置您的API密钥。")
    sys.exit(1)

from novel_generator.agents.world_builder_agent import WorldBuilderAgent
from novel_generator.agents.character_creator_agent import CharacterCreatorAgent
from novel_generator.agents.plot_designer_agent import PlotDesignerAgent
from novel_generator.agents.content_creator_agent import ContentCreatorAgent
from novel_generator.storage.json_storage import JsonStorage
from novel_generator.models.world import World
from novel_generator.models.character import Character
from novel_generator.models.plot import Plot
from novel_generator.llm.gemini import GeminiLLM


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
        # 创建LLM实例
        model_name = getattr(config, "GEMINI_MODEL", "gemini-1.5-pro")
        console.print(f"[blue]使用模型: {model_name}[/blue]")
        console.print(f"[blue]使用模型API: {config.GEMINI_API_KEY}[/blue]")
        llm = GeminiLLM(
            api_key=config.GEMINI_API_KEY,
            model_name=model_name,
            generation_config={
                "temperature": getattr(config, "TEMPERATURE", 0.7),
                "top_p": getattr(config, "TOP_P", 0.95)
            }
        )
        
        # 创建世界构建代理
        agent = WorldBuilderAgent(llm=llm)
        
        # 生成世界
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
    
    except ValueError as e:
        console.print(f"[bold red]错误: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]创建世界观时出错: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        return None


async def list_worlds(storage: JsonStorage):
    """列出所有已创建的世界观"""
    worlds = storage.list("worlds")
    
    if not worlds:
        console.print("[yellow]还没有创建任何世界观[/yellow]")
        return None
    
    console.print(Panel.fit("已创建的世界观", title="世界列表", border_style="blue"))
    
    for i, world in enumerate(worlds, 1):
        console.print(f"[blue]{i}.[/blue] {world.get('name', '未命名')} (ID: {world.get('id', 'unknown')})")
    
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


async def create_character(storage: JsonStorage, world: World):
    """创建新的角色设定"""
    if not world:
        console.print("[yellow]请先选择或创建一个世界观[/yellow]")
        return None
    
    console.print(Panel.fit("创建新的角色", title="角色创建", border_style="purple"))
    
    description = Prompt.ask("\n请描述您想要的角色\n(例如：一位天赋异禀但性格孤僻的少年，来自边远山村...)\n")
    
    if not description:
        console.print("[yellow]描述为空，将生成随机角色...[/yellow]")
        description = "随机生成一个符合该世界观的有趣角色，要有独特性格和背景故事"
    
    console.print("[bold green]正在生成角色，这可能需要一些时间...[/bold green]")
    
    try:
        # 创建LLM实例
        model_name = getattr(config, "GEMINI_MODEL", "gemini-1.5-pro")
        llm = GeminiLLM(
            api_key=config.GEMINI_API_KEY,
            model_name=model_name,
            generation_config={
                "temperature": getattr(config, "TEMPERATURE", 0.7),
                "top_p": getattr(config, "TOP_P", 0.95)
            }
        )
        
        # 创建角色创建代理
        agent = CharacterCreatorAgent(llm=llm)
        
        # 生成角色
        character = await agent.create_character(world, description)
        
        # 保存角色
        storage.save(character.to_dict(), "characters", character.id)
        
        # 打印角色摘要
        console.print(Panel(character.get_summary(), 
                            title=f"角色：{character.name}", 
                            border_style="purple",
                            expand=False))
        
        console.print(f"[green]角色已保存! ID: {character.id}[/green]")
        
        return character
    
    except ValueError as e:
        console.print(f"[bold red]错误: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]创建角色时出错: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        return None


async def list_characters(storage: JsonStorage, world: World):
    """列出指定世界观下的所有已创建角色"""
    if not world:
        console.print("[yellow]请先选择或创建一个世界观[/yellow]")
        return None
    
    characters = storage.list("characters")
    
    # 筛选指定世界观下的角色
    world_characters = [c for c in characters if c.get('world_id') == world.id]
    
    if not world_characters:
        console.print(f"[yellow]在世界「{world.name}」中还没有创建任何角色[/yellow]")
        return None
    
    console.print(Panel.fit(f"「{world.name}」世界的角色", title="角色列表", border_style="purple"))
    
    for i, character in enumerate(world_characters, 1):
        role = "未知角色"
        if "basic_info" in character and isinstance(character["basic_info"], dict) and "role" in character["basic_info"]:
            role = character["basic_info"]["role"]
        console.print(f"[purple]{i}.[/purple] {character.get('name', '未命名')} - {role} (ID: {character.get('id', 'unknown')})")
    
    index = Prompt.ask("请选择一个角色（输入序号）", default="1")
    try:
        index = int(index) - 1
        if 0 <= index < len(world_characters):
            character_data = storage.load("characters", world_characters[index]["id"])
            character = Character.from_dict(character_data)
            
            # 打印角色摘要
            console.print(Panel(character.get_summary(), 
                                title=f"角色：{character.name}", 
                                border_style="purple",
                                expand=False))
            
            return character
        else:
            console.print("[yellow]无效的选择[/yellow]")
            return None
    except ValueError:
        console.print("[yellow]请输入有效的数字[/yellow]")
        return None


async def select_multiple_characters(storage: JsonStorage, world: World):
    """选择多个角色"""
    if not world:
        console.print("[yellow]请先选择或创建一个世界观[/yellow]")
        return []
    
    characters = storage.list("characters")
    
    # 筛选指定世界观下的角色
    world_characters = [c for c in characters if c.get('world_id') == world.id]
    
    if not world_characters:
        console.print(f"[yellow]在世界「{world.name}」中还没有创建任何角色[/yellow]")
        return []
    
    console.print(Panel.fit(f"「{world.name}」世界的角色", title="角色列表", border_style="purple"))
    
    # 显示角色列表
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim")
    table.add_column("名称")
    table.add_column("角色定位")
    
    for i, character in enumerate(world_characters, 1):
        role = "未知角色"
        if "basic_info" in character and isinstance(character["basic_info"], dict) and "role" in character["basic_info"]:
            role = character["basic_info"]["role"]
        table.add_row(
            str(i), 
            character.get('name', '未命名'), 
            role
        )
    
    console.print(table)
    
    # 选择角色
    selected_indices = Prompt.ask("请选择角色（输入序号，用逗号分隔多个序号）", default="1")
    
    selected_characters = []
    try:
        for index in selected_indices.split(','):
            index = int(index.strip()) - 1
            if 0 <= index < len(world_characters):
                character_data = storage.load("characters", world_characters[index]["id"])
                character = Character.from_dict(character_data)
                selected_characters.append(character)
                console.print(f"[green]已选择角色: {character.name}[/green]")
            else:
                console.print(f"[yellow]无效的序号: {index+1}[/yellow]")
    except ValueError:
        console.print("[yellow]请输入有效的数字[/yellow]")
    
    return selected_characters


async def create_plot(storage: JsonStorage, world: World, characters: List[Character]):
    """创建新的剧情"""
    if not world:
        console.print("[yellow]请先选择或创建一个世界观[/yellow]")
        return None
    
    if not characters:
        console.print("[yellow]请先创建至少一个角色[/yellow]")
        return None
    
    console.print(Panel.fit("创建新的剧情", title="剧情设计", border_style="cyan"))
    
    # 显示已选角色
    console.print("[bold]已选择的角色：[/bold]")
    for i, character in enumerate(characters, 1):
        role = "未知角色"
        if hasattr(character, "basic_info") and character.basic_info and "role" in character.basic_info:
            role = character.basic_info["role"]
        console.print(f"[cyan]{i}.[/cyan] {character.name} - {role}")
    
    description = Prompt.ask("\n请描述您想要的剧情\n(例如：主角在修炼过程中发现一个远古秘密，踏上寻找真相的旅程...)\n")
    
    if not description:
        console.print("[yellow]描述为空，已取消创建[/yellow]")
        return None
    
    console.print("[bold green]正在生成剧情，这可能需要一些时间...[/bold green]")
    
    try:
        # 创建LLM实例
        model_name = getattr(config, "GEMINI_MODEL", "gemini-1.5-pro")
        llm = GeminiLLM(
            api_key=config.GEMINI_API_KEY,
            model_name=model_name,
            generation_config={
                "temperature": getattr(config, "TEMPERATURE", 0.7),
                "top_p": getattr(config, "TOP_P", 0.95)
            }
        )
        
        # 创建剧情设计代理
        agent = PlotDesignerAgent(llm=llm)
        
        # 生成剧情
        plot = await agent.create_plot(world, characters, description)
        
        # 保存剧情
        storage.save(plot.to_dict(), "plots", plot.id)
        
        # 打印剧情摘要
        console.print(Panel(plot.get_summary(), 
                            title=f"剧情：{plot.title}", 
                            border_style="cyan",
                            expand=False))
        
        console.print(f"[green]剧情已保存! ID: {plot.id}[/green]")
        
        return plot
    
    except ValueError as e:
        console.print(f"[bold red]错误: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]创建剧情时出错: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        return None


async def list_plots(storage: JsonStorage, world: World):
    """列出指定世界观下的所有已创建剧情"""
    if not world:
        console.print("[yellow]请先选择或创建一个世界观[/yellow]")
        return None
    
    plots = storage.list("plots")
    
    # 筛选指定世界观下的剧情
    world_plots = [p for p in plots if p.get('world_id') == world.id]
    
    if not world_plots:
        console.print(f"[yellow]在世界「{world.name}」中还没有创建任何剧情[/yellow]")
        return None
    
    console.print(Panel.fit(f"「{world.name}」世界的剧情", title="剧情列表", border_style="cyan"))
    
    for i, plot in enumerate(world_plots, 1):
        console.print(f"[cyan]{i}.[/cyan] {plot.get('title', '未命名剧情')} (ID: {plot.get('id', 'unknown')})")
    
    index = Prompt.ask("请选择一个剧情（输入序号）", default="1")
    try:
        index = int(index) - 1
        if 0 <= index < len(world_plots):
            plot_data = storage.load("plots", world_plots[index]["id"])
            plot = Plot.from_dict(plot_data)
            
            # 打印剧情摘要
            console.print(Panel(plot.get_summary(), 
                                title=f"剧情：{plot.title}", 
                                border_style="cyan",
                                expand=False))
            
            return plot
        else:
            console.print("[yellow]无效的选择[/yellow]")
            return None
    except ValueError:
        console.print("[yellow]请输入有效的数字[/yellow]")
        return None


async def generate_chapter(storage: JsonStorage, world: World, plot: Plot):
    """生成小说章节内容"""
    if not world or not plot:
        console.print("[yellow]请先选择世界观和剧情[/yellow]")
        return
    
    # 获取该世界下的所有角色
    characters = storage.list("characters")
    world_characters = [Character.from_dict(storage.load("characters", c["id"])) 
                       for c in characters if c.get('world_id') == world.id]
    
    if not world_characters:
        console.print(f"[yellow]在世界「{world.name}」中还没有创建任何角色，请先创建角色[/yellow]")
        return
    
    # 显示章节列表
    console.print(Panel.fit(f"「{plot.title}」的章节", title="章节列表", border_style="green"))
    
    for i, chapter in enumerate(plot.chapters, 1):
        console.print(f"[green]{i}.[/green] {chapter.get('title', f'第{i}章')}")
    
    chapter_index = Prompt.ask("请选择要生成的章节（输入序号）", default="1")
    try:
        chapter_index = int(chapter_index) - 1
        if 0 <= chapter_index < len(plot.chapters):
            chapter = plot.chapters[chapter_index]
            
            console.print(f"[bold]即将生成章节：[/bold] {chapter.get('title', f'第{chapter_index+1}章')}")
            console.print(f"[bold]章节概要：[/bold] {chapter.get('summary', '无概要')}")
            
            if Confirm.ask("是否继续生成？"):
                console.print("[bold green]正在生成章节内容，这可能需要一些时间...[/bold green]")
                
                # 创建LLM实例
                model_name = getattr(config, "GEMINI_MODEL", "gemini-1.5-pro")
                llm = GeminiLLM(
                    api_key=config.GEMINI_API_KEY,
                    model_name=model_name,
                    generation_config={
                        "temperature": getattr(config, "TEMPERATURE", 0.7),
                        "top_p": getattr(config, "TOP_P", 0.95)
                    }
                )
                
                # 创建内容创建代理
                agent = ContentCreatorAgent(llm=llm)
                
                # 生成章节内容
                chapter_content = await agent.create_chapter_content(plot, world, world_characters, chapter_index)
                
                # 保存章节内容
                if not os.path.exists(f"{storage.base_dir}/chapters"):
                    os.makedirs(f"{storage.base_dir}/chapters")
                
                chapter_id = f"{plot.id}_{chapter_index}"
                storage.save(chapter_content, "chapters", chapter_id)
                
                # 显示章节内容预览
                title = chapter_content.get("title", f"第{chapter_index+1}章")
                content = chapter_content.get("content", "")
                preview = content[:500] + "..." if len(content) > 500 else content
                
                console.print(Panel(preview, 
                                   title=f"章节预览：{title}", 
                                   border_style="green",
                                   expand=False))
                
                # 保存为文本文件
                output_dir = f"{storage.base_dir}/output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                filename = f"{output_dir}/{plot.title}_{title}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"# {title}\n\n")
                    f.write(content)
                
                console.print(f"[green]章节内容已保存至: {filename}[/green]")
        else:
            console.print("[yellow]无效的章节索引[/yellow]")
    except ValueError:
        console.print("[yellow]请输入有效的数字[/yellow]")
    except Exception as e:
        console.print(f"[bold red]生成章节时出错: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())


async def main_menu():
    """主菜单"""
    storage = JsonStorage(base_dir=getattr(config, "DATA_DIR", "./data"))
    
    console.print(Panel.fit(
        "欢迎使用智能中文网络小说生成系统 v0.2.0",
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
        console.print("3. 角色管理")
        console.print("4. 剧情管理")
        console.print("5. 生成小说内容")
        console.print("0. 退出")
        
        choice = Prompt.ask("请选择", choices=["0", "1", "2", "3", "4", "5"], default="1")
        
        if choice == "0":
            if Confirm.ask("确定要退出吗?"):
                break
        
        elif choice == "1":
            current_world = await create_world(storage)
        
        elif choice == "2":
            current_world = await list_worlds(storage)
        
        elif choice == "3":
            if not current_world:
                current_world = await list_worlds(storage)
                if not current_world:
                    continue
            
            console.print("\n[bold purple]===== 角色管理 =====[/bold purple]")
            console.print("1. 创建新角色")
            console.print("2. 查看已有角色")
            console.print("0. 返回")
            
            sub_choice = Prompt.ask("请选择", choices=["0", "1", "2"], default="1")
            
            if sub_choice == "1":
                await create_character(storage, current_world)
            elif sub_choice == "2":
                await list_characters(storage, current_world)
        
        elif choice == "4":
            if not current_world:
                current_world = await list_worlds(storage)
                if not current_world:
                    continue
            
            console.print("\n[bold cyan]===== 剧情管理 =====[/bold cyan]")
            console.print("1. 创建新剧情")
            console.print("2. 查看已有剧情")
            console.print("0. 返回")
            
            sub_choice = Prompt.ask("请选择", choices=["0", "1", "2"], default="1")
            
            if sub_choice == "1":
                characters = await select_multiple_characters(storage, current_world)
                if characters:
                    await create_plot(storage, current_world, characters)
            elif sub_choice == "2":
                await list_plots(storage, current_world)
        
        elif choice == "5":
            if not current_world:
                current_world = await list_worlds(storage)
                if not current_world:
                    continue
            
            plot = await list_plots(storage, current_world)
            if plot:
                await generate_chapter(storage, current_world, plot)


if __name__ == "__main__":
    # 确保数据目录存在
    data_dir = getattr(config, "DATA_DIR", "./data")
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        console.print("\n[bold red]程序已中断[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]发生错误: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
    
    console.print("[bold blue]感谢使用，再见！[/bold blue]") 