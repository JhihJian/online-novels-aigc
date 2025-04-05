"""
世界构建代理模块，用于与LLM交互生成世界观。
"""

import json
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from novel_generator.models.world import World
from novel_generator.llm.base import BaseLLM


class WorldBuilderAgent:
    """世界构建代理，负责与LLM交互生成世界观"""
    
    def __init__(self, llm: BaseLLM):
        """
        初始化世界构建代理。
        
        Args:
            llm: 语言模型接口
        """
        self.llm = llm
    
    async def create_world(self, description: str) -> World:
        """
        创建新的世界观。
        
        Args:
            description: 世界的基本描述
            
        Returns:
            创建的世界对象
        """
        # 构建提示词
        prompt = self._build_world_prompt(description)
        
        # 调用LLM获取世界观
        response = await self.llm.generate(prompt)
        
        # 解析LLM响应
        world_data = self._parse_world_response(response, description)
        
        # 创建世界对象
        world = World(
            name=world_data.get("name", "未命名世界"),
            description=description,
            background=world_data.get("background", ""),
            natural_laws=world_data.get("natural_laws", []),
            cultures=world_data.get("cultures", []),
            history=world_data.get("history", ""),
            regions=world_data.get("regions", []),
            notable_figures=world_data.get("notable_figures", []),
            magic_systems=world_data.get("magic_systems", []),
            technologies=world_data.get("technologies", []),
            id=str(uuid.uuid4()),
            created_at=datetime.now().isoformat()
        )
        
        return world
    
    async def extend_world(self, world: World, aspect: str) -> World:
        """
        扩展现有世界的特定方面。
        
        Args:
            world: 要扩展的世界对象
            aspect: 要扩展的方面，例如"历史"、"文化"等
            
        Returns:
            更新后的世界对象
        """
        # 构建提示词
        prompt = self._build_extension_prompt(world, aspect)
        
        # 调用LLM获取扩展内容
        response = await self.llm.generate(prompt)
        
        # 解析LLM响应
        updated_world = self._update_world_aspect(world, aspect, response)
        
        return updated_world
    
    def _build_world_prompt(self, description: str) -> str:
        """
        构建创建世界的提示词。
        
        Args:
            description: 世界的基本描述
            
        Returns:
            完整的提示词
        """
        return f"""你是一个专业的中文小说世界观设计师，请根据以下描述创建一个详细、连贯且有创意的世界观。请提供JSON格式的回答。

用户描述：
{description}

请包含以下内容：
1. 世界名称(name)：为这个世界取一个独特且贴合主题的名称
2. 背景(background)：世界的总体背景描述
3. 自然法则(natural_laws)：世界中的物理、魔法或其他规则
4. 文化(cultures)：主要文化及其特点
5. 历史(history)：世界的关键历史事件
6. 地域(regions)：主要地域及其特点
7. 重要人物(notable_figures)：历史或当前的重要人物
8. 魔法系统(magic_systems)：如有魔法，请描述其系统和规则
9. 技术(technologies)：世界中的技术水平和特殊技术

请以JSON格式回答，使用中文，确保内容既有创意又与用户描述一致。"""
    
    def _build_extension_prompt(self, world: World, aspect: str) -> str:
        """
        构建扩展世界特定方面的提示词。
        
        Args:
            world: 要扩展的世界对象
            aspect: 要扩展的方面
            
        Returns:
            完整的提示词
        """
        world_summary = world.get_summary()
        
        return f"""你是一个专业的中文小说世界观设计师，请为现有世界扩展"{aspect}"方面的内容。请提供JSON格式的回答。

当前世界概要：
{world_summary}

请详细扩展世界的"{aspect}"内容，使其更加丰富、具体和有创意。内容应与现有世界观保持一致，同时增加深度和细节。

请以JSON格式回答，键名为"{aspect}"，值为扩展后的内容。使用中文，确保内容既有创意又与现有世界观一致。"""
    
    def _parse_world_response(self, response: str, description: str) -> Dict[str, Any]:
        """
        解析LLM的世界创建响应。
        
        Args:
            response: LLM的响应文本
            description: 原始世界描述，用于回退
            
        Returns:
            解析后的世界数据
        """
        try:
            # 尝试从响应中提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                world_data = json.loads(json_str)
                return world_data
            else:
                # 如果没有找到JSON，使用默认结构
                return {
                    "name": "未命名世界",
                    "description": description,
                    "background": response[:1000] if len(response) > 1000 else response
                }
        except json.JSONDecodeError:
            # JSON解析失败，使用默认结构
            return {
                "name": "未命名世界",
                "description": description,
                "background": response[:1000] if len(response) > 1000 else response
            }
    
    def _update_world_aspect(self, world: World, aspect: str, response: str) -> World:
        """
        根据LLM响应更新世界的特定方面。
        
        Args:
            world: 要更新的世界对象
            aspect: 更新的方面
            response: LLM的响应
            
        Returns:
            更新后的世界对象
        """
        try:
            # 尝试从响应中提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                update_data = json.loads(json_str)
                
                # 映射aspect到world的属性
                aspect_mapping = {
                    "背景": "background",
                    "自然法则": "natural_laws",
                    "文化": "cultures",
                    "历史": "history",
                    "地域": "regions",
                    "重要人物": "notable_figures",
                    "魔法系统": "magic_systems",
                    "技术": "technologies"
                }
                
                # 更新对应的属性
                english_aspect = aspect_mapping.get(aspect, aspect)
                if english_aspect in update_data:
                    setattr(world, english_aspect, update_data[english_aspect])
                elif aspect in update_data:
                    setattr(world, english_aspect, update_data[aspect])
            
            return world
            
        except (json.JSONDecodeError, AttributeError):
            # 解析失败，返回原始世界对象
            return world 