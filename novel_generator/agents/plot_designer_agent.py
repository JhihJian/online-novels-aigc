"""
剧情设计代理模块，用于与LLM交互生成剧情。
"""

import json
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from novel_generator.models.plot import Plot
from novel_generator.models.world import World
from novel_generator.models.character import Character
from novel_generator.llm.base import BaseLLM


class PlotDesignerAgent:
    """剧情设计代理，负责与LLM交互生成剧情"""
    
    def __init__(self, llm: BaseLLM):
        """
        初始化剧情设计代理。
        
        Args:
            llm: 语言模型接口
        """
        self.llm = llm
    
    async def create_plot(self, world: World, characters: List[Character], description: str) -> Plot:
        """
        创建新的剧情。
        
        Args:
            world: 剧情所属的世界
            characters: 参与剧情的角色列表
            description: 剧情的基本描述
            
        Returns:
            创建的剧情对象
        """
        # 构建提示词
        prompt = self._build_plot_prompt(world, characters, description)
        
        # 调用LLM获取剧情
        response = await self.llm.generate(prompt)
        
        # 解析LLM响应
        plot_data = self._parse_plot_response(response, description)
        
        # 创建剧情对象
        plot = Plot(
            title=plot_data.get("title", "未命名剧情"),
            world_id=world.id,
            background=plot_data.get("background", ""),
            main_plot=plot_data.get("main_plot", ""),
            turning_points=plot_data.get("turning_points", []),
            chapters=plot_data.get("chapters", []),
            id=str(uuid.uuid4()),
            created_at=datetime.now().isoformat()
        )
        
        return plot
    
    async def generate_chapter_outline(self, plot: Plot, chapter_index: int) -> Dict[str, Any]:
        """
        生成章节大纲。
        
        Args:
            plot: 剧情对象
            chapter_index: 章节索引
            
        Returns:
            章节大纲数据
        """
        # 构建提示词
        prompt = self._build_chapter_prompt(plot, chapter_index)
        
        # 调用LLM获取章节大纲
        response = await self.llm.generate(prompt)
        
        # 解析LLM响应
        chapter_data = self._parse_chapter_response(response, chapter_index)
        
        return chapter_data
    
    async def extend_plot(self, plot: Plot, world: World, characters: List[Character], aspect: str) -> Plot:
        """
        扩展现有剧情的特定方面。
        
        Args:
            plot: 要扩展的剧情对象
            world: 剧情所属的世界
            characters: 参与剧情的角色列表
            aspect: 要扩展的方面，例如"主线"、"转折点"等
            
        Returns:
            更新后的剧情对象
        """
        # 构建提示词
        prompt = self._build_extension_prompt(plot, world, characters, aspect)
        
        # 调用LLM获取扩展内容
        response = await self.llm.generate(prompt)
        
        # 解析LLM响应
        updated_plot = self._update_plot_aspect(plot, aspect, response)
        
        return updated_plot
    
    def _build_plot_prompt(self, world: World, characters: List[Character], description: str) -> str:
        """
        构建创建剧情的提示词。
        
        Args:
            world: 剧情所属的世界
            characters: 参与剧情的角色列表
            description: 剧情的基本描述
            
        Returns:
            完整的提示词
        """
        world_summary = world.get_summary()
        
        characters_summary = ""
        for i, character in enumerate(characters):
            characters_summary += f"\n角色{i+1}：{character.get_summary()}\n"
        
        return f"""你是一个专业的中文小说剧情设计师，请根据以下世界观、角色和剧情描述创建一个详细、吸引人且有深度的剧情。请提供JSON格式的回答。

世界观概要：
{world_summary}

角色概要：
{characters_summary}

剧情描述：
{description}

请包含以下内容：
1. 剧情标题(title)：为这个剧情取一个引人入胜的标题
2. 背景(background)：剧情的时代背景和环境描述
3. 主线(main_plot)：整个剧情的核心故事线
4. 转折点(turning_points)：剧情中的关键转折点，以数组形式提供
5. 章节(chapters)：剧情划分的章节大纲，每个章节应包含标题(title)和概要(summary)，以数组形式提供

请以JSON格式回答，使用中文，确保内容既有创意又与世界观、角色设定和用户描述一致。剧情应该具有合理的结构和节奏，同时保持内在的一致性和吸引力。"""
    
    def _build_chapter_prompt(self, plot: Plot, chapter_index: int) -> str:
        """
        构建生成章节大纲的提示词。
        
        Args:
            plot: 剧情对象
            chapter_index: 章节索引
            
        Returns:
            完整的提示词
        """
        plot_summary = plot.get_summary()
        
        # 获取当前章节信息
        chapter_info = ""
        if 0 <= chapter_index < len(plot.chapters):
            chapter = plot.chapters[chapter_index]
            chapter_info = f"章节标题：{chapter.get('title', '')}\n章节概要：{chapter.get('summary', '')}"
        else:
            chapter_info = f"这是第{chapter_index+1}章，请根据剧情安排合理设计这一章节的内容。"
        
        # 获取前后章节信息作为上下文
        context = ""
        if chapter_index > 0 and chapter_index - 1 < len(plot.chapters):
            prev_chapter = plot.chapters[chapter_index - 1]
            context += f"上一章：{prev_chapter.get('title', '')}\n{prev_chapter.get('summary', '')}\n\n"
            
        if chapter_index + 1 < len(plot.chapters):
            next_chapter = plot.chapters[chapter_index + 1]
            context += f"下一章：{next_chapter.get('title', '')}\n{next_chapter.get('summary', '')}"
        
        return f"""你是一个专业的中文小说剧情设计师，请为以下剧情的第{chapter_index+1}章生成详细的章节大纲。请提供JSON格式的回答。

剧情概要：
{plot_summary}

当前章节信息：
{chapter_info}

相邻章节上下文：
{context}

请包含以下内容：
1. 章节标题(title)：为这个章节取一个贴合内容的标题
2. 章节概要(summary)：章节的整体内容概括
3. 场景(scenes)：章节中的各个场景，每个场景包含场景描述(description)和对话/行动要点(key_points)，以数组形式提供
4. 角色情感(character_arcs)：主要角色在本章的情感变化和成长
5. 冲突(conflicts)：本章中的主要冲突和矛盾
6. 连接(connections)：本章与整体剧情的连接点

请以JSON格式回答，使用中文，确保内容既有创意又与整体剧情保持一致。章节大纲应该既能独立成章，又能自然地融入整个故事。"""
    
    def _build_extension_prompt(self, plot: Plot, world: World, characters: List[Character], aspect: str) -> str:
        """
        构建扩展剧情特定方面的提示词。
        
        Args:
            plot: 要扩展的剧情对象
            world: 剧情所属的世界
            characters: 参与剧情的角色列表
            aspect: 要扩展的方面
            
        Returns:
            完整的提示词
        """
        plot_summary = plot.get_summary()
        world_summary = world.get_summary()
        
        characters_summary = ""
        for i, character in enumerate(characters):
            characters_summary += f"\n角色{i+1}：{character.get_summary()}\n"
        
        return f"""你是一个专业的中文小说剧情设计师，请为现有剧情扩展"{aspect}"方面的内容。请提供JSON格式的回答。

世界观概要：
{world_summary}

角色概要：
{characters_summary}

当前剧情概要：
{plot_summary}

请详细扩展剧情的"{aspect}"内容，使其更加丰富、具体和有创意。内容应与现有剧情设定和世界观保持一致，同时增加深度和细节。

请以JSON格式回答，键名为"{aspect}"，值为扩展后的内容。使用中文，确保内容既有创意又与现有剧情设定和世界观一致。"""
    
    def _parse_plot_response(self, response: str, description: str) -> Dict[str, Any]:
        """
        解析LLM的剧情创建响应。
        
        Args:
            response: LLM的响应文本
            description: 原始剧情描述，用于回退
            
        Returns:
            解析后的剧情数据
        """
        try:
            # 尝试从响应中提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                plot_data = json.loads(json_str)
                return plot_data
            else:
                # 如果没有找到JSON，使用默认结构
                return {
                    "title": "未命名剧情",
                    "background": description,
                    "main_plot": description,
                    "chapters": [{"title": "第一章", "summary": description}]
                }
        except json.JSONDecodeError:
            # JSON解析失败，使用默认结构
            return {
                "title": "未命名剧情",
                "background": description,
                "main_plot": description,
                "chapters": [{"title": "第一章", "summary": description}]
            }
    
    def _parse_chapter_response(self, response: str, chapter_index: int) -> Dict[str, Any]:
        """
        解析LLM的章节大纲响应。
        
        Args:
            response: LLM的响应文本
            chapter_index: 章节索引，用于回退
            
        Returns:
            解析后的章节数据
        """
        try:
            # 尝试从响应中提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                chapter_data = json.loads(json_str)
                return chapter_data
            else:
                # 如果没有找到JSON，使用默认结构
                return {
                    "title": f"第{chapter_index+1}章",
                    "summary": response[:500] if len(response) > 500 else response
                }
        except json.JSONDecodeError:
            # JSON解析失败，使用默认结构
            return {
                "title": f"第{chapter_index+1}章",
                "summary": response[:500] if len(response) > 500 else response
            }
    
    def _update_plot_aspect(self, plot: Plot, aspect: str, response: str) -> Plot:
        """
        根据LLM响应更新剧情的特定方面。
        
        Args:
            plot: 要更新的剧情对象
            aspect: 更新的方面
            response: LLM的响应
            
        Returns:
            更新后的剧情对象
        """
        try:
            # 尝试从响应中提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                update_data = json.loads(json_str)
                
                # 映射aspect到plot的属性
                aspect_mapping = {
                    "标题": "title",
                    "背景": "background",
                    "主线": "main_plot",
                    "转折点": "turning_points",
                    "章节": "chapters"
                }
                
                # 更新对应的属性
                english_aspect = aspect_mapping.get(aspect, aspect)
                if english_aspect in update_data:
                    setattr(plot, english_aspect, update_data[english_aspect])
                elif aspect in update_data:
                    setattr(plot, english_aspect, update_data[aspect])
            
            return plot
            
        except (json.JSONDecodeError, AttributeError):
            # 解析失败，返回原始剧情对象
            return plot 