"""
章节写作代理模块，用于与LLM交互生成章节内容。
"""

import json
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from novel_generator.models.plot import Plot
from novel_generator.models.world import World
from novel_generator.models.character import Character
from novel_generator.llm.base import BaseLLM


class ChapterWriterAgent:
    """章节写作代理，负责与LLM交互生成章节内容"""
    
    def __init__(self, llm: BaseLLM):
        """
        初始化章节写作代理。
        
        Args:
            llm: 语言模型接口
        """
        self.llm = llm
    
    async def write_chapter(self, plot: Plot, world: World, characters: List[Character], chapter_index: int) -> str:
        """
        写作章节内容。
        
        Args:
            plot: 剧情对象
            world: 世界对象
            characters: 角色列表
            chapter_index: 章节索引
            
        Returns:
            生成的章节内容
        """
        if chapter_index < 0 or chapter_index >= len(plot.chapters):
            raise ValueError(f"章节索引 {chapter_index} 超出范围")
        
        # 获取章节大纲
        chapter_outline = plot.get_chapter(chapter_index)
        if not chapter_outline:
            raise ValueError(f"找不到索引为 {chapter_index} 的章节")
        
        # 构建提示词
        prompt = self._build_chapter_prompt(plot, world, characters, chapter_outline, chapter_index)
        
        # 调用LLM生成章节内容
        response = await self.llm.generate(prompt)
        
        # 处理和格式化章节内容
        chapter_content = self._format_chapter_content(response, chapter_outline)
        
        return chapter_content
    
    async def revise_chapter(self, chapter_content: str, plot: Plot, world: World, characters: List[Character], suggestions: str) -> str:
        """
        修改章节内容。
        
        Args:
            chapter_content: 原始章节内容
            plot: 剧情对象
            world: 世界对象
            characters: 角色列表
            suggestions: 修改建议
            
        Returns:
            修改后的章节内容
        """
        # 构建提示词
        prompt = self._build_revision_prompt(chapter_content, plot, world, characters, suggestions)
        
        # 调用LLM生成修改后的章节内容
        response = await self.llm.generate(prompt)
        
        # 处理和格式化修改后的章节内容
        revised_content = self._format_revision_content(response)
        
        return revised_content
    
    def _build_chapter_prompt(self, plot: Plot, world: World, characters: List[Character], chapter_outline: Dict[str, Any], chapter_index: int) -> str:
        """
        构建章节写作的提示词。
        
        Args:
            plot: 剧情对象
            world: 世界对象
            characters: 角色列表
            chapter_outline: 章节大纲
            chapter_index: 章节索引
            
        Returns:
            完整的提示词
        """
        world_summary = world.get_summary()
        plot_summary = plot.get_summary()
        
        characters_summary = ""
        for i, character in enumerate(characters):
            characters_summary += f"\n角色{i+1}：{character.name}\n{character.get_summary()}\n"
        
        # 获取前一章的内容摘要，如果有的话
        previous_chapter_summary = ""
        if chapter_index > 0:
            prev_chapter = plot.get_chapter(chapter_index - 1)
            if prev_chapter:
                previous_chapter_summary = f"\n前一章内容摘要：\n标题：{prev_chapter.get('title', '')}\n{prev_chapter.get('summary', '')}"
        
        # 获取当前章节的详细大纲
        scenes = ""
        if "scenes" in chapter_outline:
            for i, scene in enumerate(chapter_outline["scenes"]):
                scenes += f"\n场景{i+1}：{scene.get('description', '')}\n"
                if "key_points" in scene:
                    for j, point in enumerate(scene["key_points"]):
                        scenes += f"  要点{j+1}：{point}\n"
        
        conflicts = ""
        if "conflicts" in chapter_outline:
            conflicts = f"\n冲突：\n{chapter_outline['conflicts']}"
        
        character_arcs = ""
        if "character_arcs" in chapter_outline:
            character_arcs = f"\n角色情感变化：\n{chapter_outline['character_arcs']}"
        
        return f"""你是一个专业的中文小说写作助手，请根据以下信息为小说写作第{chapter_index+1}章内容。请创作吸引人、生动、有深度的章节内容，包含丰富的描写和对话。

世界观概要：
{world_summary}

剧情概要：
{plot_summary}

角色概要：
{characters_summary}
{previous_chapter_summary}

当前章节信息：
标题：{chapter_outline.get('title', '')}
概要：{chapter_outline.get('summary', '')}
{scenes}
{conflicts}
{character_arcs}

请根据上述信息创作完整的小说章节，要求：
1. 文风要优美流畅，富有文学性
2. 按照章节概要和场景安排展开情节
3. 注重角色性格的表现和情感的发展
4. 对话要自然，符合角色身份和语言习惯
5. 适当加入环境描写和人物心理活动描写
6. 保持与世界观和整体剧情的一致性
7. 内容不要过于概括，请展开细节，创作完整的场景
8. 适当使用悬念和伏笔，增强章节的吸引力

请直接输出完整的章节内容，无需添加额外的解释。内容应包含章节标题、分段落的正文，总字数在3000-5000字之间。"""
    
    def _build_revision_prompt(self, chapter_content: str, plot: Plot, world: World, characters: List[Character], suggestions: str) -> str:
        """
        构建章节修改的提示词。
        
        Args:
            chapter_content: 原始章节内容
            plot: 剧情对象
            world: 世界对象
            characters: 角色列表
            suggestions: 修改建议
            
        Returns:
            完整的提示词
        """
        world_summary = world.get_summary()[:200]  # 简化世界概要
        plot_summary = plot.get_summary()[:200]    # 简化剧情概要
        
        characters_brief = ""
        for i, character in enumerate(characters[:3]):  # 只包含前三个角色的简要信息
            characters_brief += f"\n角色{i+1}：{character.name} - {character.basic_info.get('职业', '')}"
        
        return f"""你是一个专业的中文小说编辑，请根据以下修改建议对小说章节进行修订。请保留原有内容的精华部分，同时根据建议进行适当的调整和优化。

世界观概要：
{world_summary}

剧情概要：
{plot_summary}

角色简介：
{characters_brief}

修改建议：
{suggestions}

原始章节内容：
{chapter_content}

请根据上述信息对章节内容进行修订，要求：
1. 遵循修改建议进行调整
2. 保持内容的连贯性和一致性
3. 改进文风，使其更加优美流畅
4. 加强角色性格和情感的表现
5. 优化对话，使其更加自然符合角色特点
6. 保持与世界观和整体剧情的一致性

请直接输出修订后的完整章节内容，无需添加额外的解释。"""
    
    def _format_chapter_content(self, response: str, chapter_outline: Dict[str, Any]) -> str:
        """
        格式化LLM生成的章节内容。
        
        Args:
            response: LLM的响应文本
            chapter_outline: 章节大纲
            
        Returns:
            格式化后的章节内容
        """
        # 如果响应中包含JSON格式的内容，则提取其中的"content"字段
        try:
            if response.find('{') != -1 and response.rfind('}') != -1:
                json_str = response[response.find('{'):response.rfind('}')+1]
                content_data = json.loads(json_str)
                if "content" in content_data:
                    return content_data["content"]
        except:
            pass
        
        # 否则，进行基本的格式化处理
        
        # 添加章节标题，如果响应中没有
        title = chapter_outline.get('title', '')
        if title and not response.strip().startswith(title):
            response = f"{title}\n\n{response}"
        
        return response
    
    def _format_revision_content(self, response: str) -> str:
        """
        格式化LLM修改后的章节内容。
        
        Args:
            response: LLM的响应文本
            
        Returns:
            格式化后的修改内容
        """
        # 如果响应中包含JSON格式的内容，则提取其中的"revised_content"字段
        try:
            if response.find('{') != -1 and response.rfind('}') != -1:
                json_str = response[response.find('{'):response.rfind('}')+1]
                content_data = json.loads(json_str)
                if "revised_content" in content_data:
                    return content_data["revised_content"]
        except:
            pass
        
        # 否则，直接返回原始响应
        return response 