#!/usr/bin/env python
"""
智能中文网络小说自动生成脚本
根据输入的描述，自动完成创建世界观、角色、剧情和生成小说前三章
"""

import asyncio
import sys
import os
import json
import argparse
import uuid
from typing import List, Dict, Any, Optional

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


async def create_world(storage: JsonStorage, description: str) -> Optional[World]:
    """创建新的世界观设定"""
    print(f"开始创建世界观：{description[:50]}...")
    
    try:
        # 创建LLM实例
        model_name = getattr(config, "GEMINI_MODEL", "gemini-1.5-pro")
        print(f"使用模型: {model_name}")
        
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
        
        print("正在生成世界观...")
        
        # 生成世界
        world = await agent.create_world(description)
        
        # 保存世界观
        storage.save(world.to_dict(), "worlds", world.id)
        
        # 打印世界观摘要
        print(f"\n==== 世界观：{world.name} ====")
        print(world.get_summary())
        print(f"世界观已保存! ID: {world.id}")
        
        return world
    
    except Exception as e:
        print(f"创建世界观时出错: {e}")
        import traceback
        print(traceback.format_exc())
        return None


async def create_characters(storage: JsonStorage, world: World, num_characters: int = 3) -> List[Character]:
    """创建角色"""
    if not world:
        print("错误：无法创建角色，世界观不存在")
        return []
    
    characters = []
    
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
        
        # 创建角色角色类型
        character_types = [
            "一个适合担任主角的角色，有独特的能力和背景",
            "一个重要的配角，与主角有紧密联系",
            "一个有趣的配角，性格鲜明",
            "一个具有神秘背景的角色",
            "一个强大且有智慧的角色"
        ]
        
        print(f"\n开始创建{num_characters}个角色...")
        
        # 创建指定数量的角色
        for i in range(min(num_characters, len(character_types))):
            description = f"随机生成一个符合该世界观的{character_types[i]}"
            print(f"创建角色 {i+1}: {description}")
            print(f"正在生成角色...")
            
            # 生成角色
            character = await agent.create_character(world, description)
            
            # 保存角色
            storage.save(character.to_dict(), "characters", character.id)
            
            # 打印角色摘要
            print(f"==== 角色：{character.name} ====")
            print(character.get_summary())
            print(f"角色已保存! ID: {character.id}")
            
            characters.append(character)
        
        return characters
    
    except Exception as e:
        print(f"创建角色时出错: {e}")
        import traceback
        print(traceback.format_exc())
        return characters  # 返回已创建的角色


async def create_plot(storage: JsonStorage, world: World, characters: List[Character], description: str) -> Optional[Plot]:
    """创建新的剧情"""
    if not world:
        print("错误：无法创建剧情，世界观不存在")
        return None
    
    if not characters:
        print("错误：无法创建剧情，角色列表为空")
        return None
    
    print(f"\n开始创建剧情：{description[:50]}...")
    
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
        
        print("正在生成剧情大纲和章节...")
        
        # 生成剧情
        plot = await agent.create_plot(world, characters, description)
        
        # 保存剧情
        storage.save(plot.to_dict(), "plots", plot.id)
        
        # 打印剧情摘要
        print(f"\n==== 剧情：{plot.title} ====")
        print(plot.get_summary())
        print(f"剧情已保存! ID: {plot.id}")
        
        return plot
    
    except Exception as e:
        print(f"创建剧情时出错: {e}")
        import traceback
        print(traceback.format_exc())
        return None


async def generate_chapters(storage: JsonStorage, world: World, plot: Plot, characters: List[Character], num_chapters: int = 3) -> List[Dict[str, Any]]:
    """生成小说章节内容"""
    if not world or not plot:
        print("错误：无法生成章节，世界观或剧情不存在")
        return []
    
    if not characters:
        print("错误：无法生成章节，角色列表为空")
        return []
    
    chapters = []
    
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
        
        # 创建内容创建代理
        agent = ContentCreatorAgent(llm=llm)
        
        # 确定生成章节数量，不超过剧情中定义的章节数
        chapters_to_generate = min(num_chapters, len(plot.chapters))
        print(f"\n开始生成前{chapters_to_generate}章内容...")
        
        # 确保输出目录存在
        output_dir = f"{storage.base_dir}/output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成章节内容
        for chapter_index in range(chapters_to_generate):
            chapter = plot.chapters[chapter_index]
            print(f"正在生成第{chapter_index+1}章: {chapter.get('title', f'第{chapter_index+1}章')}...")
            
            # 生成章节内容
            chapter_content = await agent.create_chapter_content(plot, world, characters, chapter_index)
            
            # 保存章节内容
            if not os.path.exists(f"{storage.base_dir}/chapters"):
                os.makedirs(f"{storage.base_dir}/chapters")
            
            chapter_id = f"{plot.id}_{chapter_index}"
            storage.save(chapter_content, "chapters", chapter_id)
            
            # 保存为文本文件
            title = chapter_content.get("title", f"第{chapter_index+1}章")
            content = chapter_content.get("content", "")
            
            filename = f"{output_dir}/{plot.title}_{title}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(content)
            
            print(f"章节{chapter_index+1}已保存至: {filename}")
            
            # 添加到结果列表
            chapters.append(chapter_content)
            
            # 短暂暂停，避免API调用过于频繁
            await asyncio.sleep(1)
        
        # 生成完整小说合集
        novel_filename = f"{output_dir}/{plot.title}_完整小说.txt"
        with open(novel_filename, "w", encoding="utf-8") as f:
            f.write(f"# {plot.title}\n\n")
            f.write(f"## 世界观：{world.name}\n\n")
            f.write(f"{world.description}\n\n")
            
            f.write("## 角色列表\n\n")
            for character in characters:
                role = ""
                if hasattr(character, "basic_info") and character.basic_info and "role" in character.basic_info:
                    role = character.basic_info["role"]
                f.write(f"- {character.name}: {role}\n")
            f.write("\n")
            
            f.write("## 剧情梗概\n\n")
            f.write(f"{plot.background}\n\n")
            
            for i, chapter_content in enumerate(chapters):
                title = chapter_content.get("title", f"第{i+1}章")
                content = chapter_content.get("content", "")
                f.write(f"## {title}\n\n")
                f.write(f"{content}\n\n")
        
        print(f"完整小说已保存至: {novel_filename}")
        
        return chapters
    
    except Exception as e:
        print(f"生成章节时出错: {e}")
        import traceback
        print(traceback.format_exc())
        return chapters  # 返回已生成的章节


async def generate_novel(description: str, num_characters: int = 3, num_chapters: int = 3) -> bool:
    """从描述生成完整小说的流程"""
    # 确保数据目录存在
    data_dir = getattr(config, "DATA_DIR", "./data")
    os.makedirs(data_dir, exist_ok=True)
    
    # 创建存储实例
    storage = JsonStorage(base_dir=data_dir)
    
    # 1. 创建世界观
    world = await create_world(storage, description)
    if not world:
        print("无法继续生成小说，世界观创建失败")
        return False
    
    # 2. 创建角色
    characters = await create_characters(storage, world, num_characters)
    if not characters:
        print("无法继续生成小说，角色创建失败")
        return False
    
    # 3. 创建剧情
    plot_description = f"基于世界观'{world.name}'和已创建的角色，创建一个有吸引力的故事情节，{description}"
    plot = await create_plot(storage, world, characters, plot_description)
    if not plot:
        print("无法继续生成小说，剧情创建失败")
        return False
    
    # 4. 生成章节内容
    chapters = await generate_chapters(storage, world, plot, characters, num_chapters)
    if not chapters:
        print("章节内容生成失败")
        return False
    
    print("\n====== 小说生成完成 ======")
    print(f"- 世界观: {world.name}")
    print(f"- 角色数量: {len(characters)}")
    print(f"- 小说标题: {plot.title}")
    print(f"- 已生成章节: {len(chapters)}")
    print(f"- 输出目录: {data_dir}/output")
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能中文网络小说自动生成脚本")
    parser.add_argument("--description", "-d", type=str, help="小说的基本描述")
    parser.add_argument("--input", "-i", type=str, help="包含小说描述的文件路径")
    parser.add_argument("--characters", "-c", type=int, default=3, help="生成的角色数量")
    parser.add_argument("--chapters", "-n", type=int, default=3, help="生成的章节数量")
    
    args = parser.parse_args()
    
    # 获取描述文本
    description = args.description
    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                description = f.read().strip()
        except Exception as e:
            print(f"读取输入文件时出错: {e}")
            sys.exit(1)
    
    if not description:
        print("错误: 必须提供小说描述，可通过--description参数直接提供或通过--input参数指定文件")
        sys.exit(1)
    
    try:
        # 运行小说生成流程
        asyncio.run(generate_novel(description, args.characters, args.chapters))
    except KeyboardInterrupt:
        print("\n程序已中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    main() 