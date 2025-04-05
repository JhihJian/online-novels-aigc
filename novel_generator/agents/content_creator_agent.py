"""
内容创建代理模块，用于与LLM交互生成小说内容。
整合了agno库的Agent功能实现更高效的交互。
"""

import json
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from agno.agent import Agent
from agno.tools import tool

from novel_generator.models.plot import Plot
from novel_generator.models.world import World
from novel_generator.models.character import Character
from novel_generator.llm.base import BaseLLM


class ContentCreatorAgent(Agent):
    """内容创建代理，负责与LLM交互生成小说具体内容，基于agno的Agent实现"""
    
    def __init__(self, llm: BaseLLM):
        """
        初始化内容创建代理。
        
        Args:
            llm: 语言模型接口
        """
        super().__init__(
            name="ContentCreatorAgent", 
            description="负责创建小说章节内容的AI代理"
        )
        self.llm = llm
        self._register_tools()
    
    def _register_tools(self):
        """注册代理可用的工具"""
        
        @tool(description="根据章节大纲生成章节内容")
        async def generate_chapter_content(plot_data: Dict[str, Any], 
                                         world_data: Dict[str, Any],
                                         characters_data: List[Dict[str, Any]], 
                                         chapter_index: int) -> Dict[str, Any]:
            """
            根据章节大纲生成章节内容。
            
            Args:
                plot_data: 剧情数据
                world_data: 世界数据
                characters_data: 角色数据列表
                chapter_index: 章节索引
                
            Returns:
                生成的章节内容数据
            """
            # 创建剧情、世界和角色对象
            plot = Plot.from_dict(plot_data)
            world = World.from_dict(world_data)
            characters = [Character.from_dict(char_data) for char_data in characters_data]
            
            # 获取章节信息
            if 0 <= chapter_index < len(plot.chapters):
                chapter = plot.chapters[chapter_index]
            else:
                raise ValueError(f"章节索引 {chapter_index} 超出范围")
                
            # 构建提示词
            prompt = self._build_chapter_prompt(plot, world, characters, chapter, chapter_index)
            
            # 调用LLM获取章节内容
            response = await self.llm.generate(prompt)
            
            # 解析LLM响应
            chapter_content = self._parse_chapter_content(response, chapter)
            
            return chapter_content
        
        @tool(description="生成特定场景内容")
        async def generate_scene_content(plot_data: Dict[str, Any], 
                                       world_data: Dict[str, Any],
                                       characters_data: List[Dict[str, Any]], 
                                       chapter_index: int,
                                       scene_description: str) -> Dict[str, Any]:
            """
            生成特定场景内容。
            
            Args:
                plot_data: 剧情数据
                world_data: 世界数据
                characters_data: 角色数据列表
                chapter_index: 章节索引
                scene_description: 场景描述
                
            Returns:
                生成的场景内容数据
            """
            # 创建剧情、世界和角色对象
            plot = Plot.from_dict(plot_data)
            world = World.from_dict(world_data)
            characters = [Character.from_dict(char_data) for char_data in characters_data]
            
            # 获取章节信息
            if 0 <= chapter_index < len(plot.chapters):
                chapter = plot.chapters[chapter_index]
            else:
                raise ValueError(f"章节索引 {chapter_index} 超出范围")
                
            # 构建提示词
            prompt = self._build_scene_prompt(plot, world, characters, chapter, scene_description)
            
            # 调用LLM获取场景内容
            response = await self.llm.generate(prompt)
            
            # 解析LLM响应
            scene_content = self._parse_scene_content(response)
            
            return scene_content
        
        @tool(description="修改和完善章节内容")
        async def refine_chapter_content(plot_data: Dict[str, Any],
                                       world_data: Dict[str, Any],
                                       characters_data: List[Dict[str, Any]],
                                       chapter_index: int, 
                                       current_content: str,
                                       refinement_instruction: str) -> Dict[str, Any]:
            """
            修改和完善章节内容。
            
            Args:
                plot_data: 剧情数据
                world_data: 世界数据
                characters_data: 角色数据列表
                chapter_index: 章节索引
                current_content: 当前章节内容
                refinement_instruction: 完善指南
                
            Returns:
                完善后的章节内容数据
            """
            # 创建剧情、世界和角色对象
            plot = Plot.from_dict(plot_data)
            world = World.from_dict(world_data)
            characters = [Character.from_dict(char_data) for char_data in characters_data]
            
            # 获取章节信息
            if 0 <= chapter_index < len(plot.chapters):
                chapter = plot.chapters[chapter_index]
            else:
                raise ValueError(f"章节索引 {chapter_index} 超出范围")
                
            # 构建提示词
            prompt = self._build_refinement_prompt(plot, world, characters, chapter, current_content, refinement_instruction)
            
            # 调用LLM获取完善后的内容
            response = await self.llm.generate(prompt)
            
            # 解析LLM响应
            refined_content = self._parse_refined_content(response)
            
            return refined_content
            
        # 直接设置tools属性
        self.tools = {
            "generate_chapter_content": generate_chapter_content,
            "generate_scene_content": generate_scene_content,
            "refine_chapter_content": refine_chapter_content
        }
    
    async def create_chapter_content(self, plot: Plot, world: World, characters: List[Character], chapter_index: int) -> Dict[str, Any]:
        """
        创建章节内容。
        
        Args:
            plot: 剧情对象
            world: 世界对象
            characters: 角色列表
            chapter_index: 章节索引
            
        Returns:
            生成的章节内容
        """
        # 获取剧情、世界和角色数据
        plot_data = plot.to_dict()
        world_data = world.to_dict()
        characters_data = [char.to_dict() for char in characters]
        
        # 调用代理的generate_chapter_content工具
        result = await self.tools["generate_chapter_content"](plot_data, world_data, characters_data, chapter_index)
        
        return result
    
    async def create_scene_content(self, plot: Plot, world: World, characters: List[Character], 
                                  chapter_index: int, scene_description: str) -> Dict[str, Any]:
        """
        创建特定场景内容。
        
        Args:
            plot: 剧情对象
            world: 世界对象
            characters: 角色列表
            chapter_index: 章节索引
            scene_description: 场景描述
            
        Returns:
            生成的场景内容
        """
        # 获取剧情、世界和角色数据
        plot_data = plot.to_dict()
        world_data = world.to_dict()
        characters_data = [char.to_dict() for char in characters]
        
        # 调用代理的generate_scene_content工具
        result = await self.tools["generate_scene_content"](plot_data, world_data, characters_data, chapter_index, scene_description)
        
        return result
    
    async def refine_content(self, plot: Plot, world: World, characters: List[Character], 
                           chapter_index: int, current_content: str, refinement_instruction: str) -> Dict[str, Any]:
        """
        修改和完善章节内容。
        
        Args:
            plot: 剧情对象
            world: 世界对象
            characters: 角色列表
            chapter_index: 章节索引
            current_content: 当前章节内容
            refinement_instruction: 完善指南
            
        Returns:
            完善后的章节内容
        """
        # 获取剧情、世界和角色数据
        plot_data = plot.to_dict()
        world_data = world.to_dict()
        characters_data = [char.to_dict() for char in characters]
        
        # 调用代理的refine_chapter_content工具
        result = await self.tools["refine_chapter_content"](plot_data, world_data, characters_data, chapter_index, 
                                                      current_content, refinement_instruction)
        
        return result
    
    def _build_chapter_prompt(self, plot: Plot, world: World, characters: List[Character], 
                             chapter: Dict[str, Any], chapter_index: int) -> str:
        """
        构建生成章节内容的提示词。
        
        Args:
            plot: 剧情对象
            world: 世界对象
            characters: 角色列表
            chapter: 章节信息
            chapter_index: 章节索引
            
        Returns:
            完整的提示词
        """
        world_summary = world.get_summary()
        
        characters_summary = ""
        for i, character in enumerate(characters):
            characters_summary += f"\n角色{i+1}：{character.get_summary()}\n"
        
        plot_summary = plot.get_summary()
        
        chapter_title = chapter.get("title", f"第{chapter_index+1}章")
        chapter_summary = chapter.get("summary", "")
        
        # 获取章节场景信息
        scenes_info = ""
        if "scenes" in chapter and isinstance(chapter["scenes"], list):
            for i, scene in enumerate(chapter["scenes"]):
                scene_desc = scene.get("description", "")
                key_points = scene.get("key_points", [])
                key_points_str = "\n".join([f"- {point}" for point in key_points]) if key_points else ""
                
                scenes_info += f"\n场景{i+1}：{scene_desc}\n关键点：\n{key_points_str}\n"
        
        # 获取前后章节信息作为上下文
        context = ""
        if chapter_index > 0 and chapter_index - 1 < len(plot.chapters):
            prev_chapter = plot.chapters[chapter_index - 1]
            context += f"上一章：{prev_chapter.get('title', '')}\n{prev_chapter.get('summary', '')}\n\n"
            
        if chapter_index + 1 < len(plot.chapters):
            next_chapter = plot.chapters[chapter_index + 1]
            context += f"下一章：{next_chapter.get('title', '')}\n{next_chapter.get('summary', '')}"
        
        return f"""你是一个专业的中文小说作家，请根据以下信息创作精彩的小说章节内容。

世界观概要：
{world_summary}

角色概要：
{characters_summary}

剧情概要：
{plot_summary}

章节信息：
标题：{chapter_title}
概要：{chapter_summary}

章节场景：
{scenes_info}

相邻章节上下文：
{context}

请根据以上信息，创作一个完整、生动、情节连贯的章节内容。内容应当忠实于剧情概要和章节概要，但可以根据需要添加细节、对话和描写，使故事更加丰富和引人入胜。请确保写作风格流畅，情节发展合理，突出角色特点，并与整体剧情保持一致。

请直接返回创作的章节内容，不需要额外的解释或说明。"""
    
    def _build_scene_prompt(self, plot: Plot, world: World, characters: List[Character], 
                           chapter: Dict[str, Any], scene_description: str) -> str:
        """
        构建生成场景内容的提示词。
        
        Args:
            plot: 剧情对象
            world: 世界对象
            characters: 角色列表
            chapter: 章节信息
            scene_description: 场景描述
            
        Returns:
            完整的提示词
        """
        world_summary = world.get_summary()
        
        # 筛选出可能出现在场景中的角色
        relevant_characters = []
        for character in characters:
            # 这里可以添加筛选逻辑，例如根据角色特点或剧情关联
            relevant_characters.append(character)
        
        characters_summary = ""
        for i, character in enumerate(relevant_characters):
            characters_summary += f"\n角色{i+1}：{character.get_summary()}\n"
        
        chapter_title = chapter.get("title", "")
        chapter_summary = chapter.get("summary", "")
        
        return f"""你是一个专业的中文小说作家，请根据以下信息创作一个精彩的小说场景。

世界观概要：
{world_summary}

相关角色：
{characters_summary}

章节信息：
标题：{chapter_title}
概要：{chapter_summary}

场景描述：
{scene_description}

请根据以上信息，创作一个生动、细腻、有代入感的场景内容。内容应当围绕场景描述展开，但可以根据需要添加细节、对话和描写，使场景更加丰富和真实。请确保写作风格流畅，场景描述贴合世界观，角色表现符合其特点，并与章节概要保持一致。

场景内容应该包含环境描写、人物动作、对话交流等元素，让读者能够身临其境地感受到场景的氛围和情绪。

请直接返回创作的场景内容，不需要额外的解释或说明。"""
    
    def _build_refinement_prompt(self, plot: Plot, world: World, characters: List[Character], 
                                chapter: Dict[str, Any], current_content: str, 
                                refinement_instruction: str) -> str:
        """
        构建完善章节内容的提示词。
        
        Args:
            plot: 剧情对象
            world: 世界对象
            characters: 角色列表
            chapter: 章节信息
            current_content: 当前章节内容
            refinement_instruction: 完善指南
            
        Returns:
            完整的提示词
        """
        world_summary = world.get_summary()
        
        characters_summary = ""
        for i, character in enumerate(characters):
            characters_summary += f"\n角色{i+1}：{character.name}\n主要特点：{character.personality}\n"
        
        chapter_title = chapter.get("title", "")
        chapter_summary = chapter.get("summary", "")
        
        return f"""你是一个专业的中文小说编辑，请根据以下信息和指导，对小说章节内容进行修改和完善。

世界观概要：
{world_summary}

相关角色：
{characters_summary}

章节信息：
标题：{chapter_title}
概要：{chapter_summary}

当前章节内容：
{current_content}

修改和完善指南：
{refinement_instruction}

请根据以上信息和指导，对当前章节内容进行修改和完善。你的修改应当尊重原有内容的基本结构和风格，同时根据完善指南进行必要的调整，提升内容质量。

修改内容时，请确保：
1. 保持情节的连贯性和逻辑性
2. 角色表现与其设定保持一致
3. 世界观元素的使用准确恰当
4. 文字表达流畅、生动
5. 解决完善指南中提出的问题或建议

请直接返回修改后的完整章节内容，不需要额外的解释或说明，也不需要标记你的修改之处。"""
    
    def _parse_chapter_content(self, response: str, chapter: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析LLM的章节内容响应。
        
        Args:
            response: LLM的响应文本
            chapter: 章节信息，用于回退
            
        Returns:
            解析后的章节内容数据
        """
        # 对于内容生成，我们主要是获取文本，所以直接返回响应
        # 但我们可以添加一些元数据
        return {
            "title": chapter.get("title", ""),
            "content": response,
            "word_count": len(response),
            "summary": chapter.get("summary", ""),
            "generated_at": datetime.now().isoformat()
        }
    
    def _parse_scene_content(self, response: str) -> Dict[str, Any]:
        """
        解析LLM的场景内容响应。
        
        Args:
            response: LLM的响应文本
            
        Returns:
            解析后的场景内容数据
        """
        # 对于场景内容，直接返回文本和一些元数据
        return {
            "content": response,
            "word_count": len(response),
            "generated_at": datetime.now().isoformat()
        }
    
    def _parse_refined_content(self, response: str) -> Dict[str, Any]:
        """
        解析LLM的完善内容响应。
        
        Args:
            response: LLM的响应文本
            
        Returns:
            解析后的完善内容数据
        """
        # 返回完善后的内容和一些元数据
        return {
            "content": response,
            "word_count": len(response),
            "refined_at": datetime.now().isoformat()
        } 