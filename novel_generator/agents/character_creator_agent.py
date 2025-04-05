"""
角色创建代理模块，用于与LLM交互生成角色。
"""

import json
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from novel_generator.models.character import Character
from novel_generator.models.world import World
from novel_generator.llm.base import BaseLLM


class CharacterCreatorAgent:
    """角色创建代理，负责与LLM交互生成角色"""
    
    def __init__(self, llm: BaseLLM):
        """
        初始化角色创建代理。
        
        Args:
            llm: 语言模型接口
        """
        self.llm = llm
    
    async def create_character(self, world: World, description: str) -> Character:
        """
        创建新的角色。
        
        Args:
            world: 角色所属的世界
            description: 角色的基本描述
            
        Returns:
            创建的角色对象
        """
        # 构建提示词
        prompt = self._build_character_prompt(world, description)
        
        # 调用LLM获取角色
        response = await self.llm.generate(prompt)
        
        # 解析LLM响应
        character_data = self._parse_character_response(response, description)
        
        # 创建角色对象
        character = Character(
            name=character_data.get("name", "未命名角色"),
            world_id=world.id,
            basic_info=character_data.get("basic_info", {}),
            appearance=character_data.get("appearance", ""),
            personality=character_data.get("personality", ""),
            background=character_data.get("background", ""),
            abilities=character_data.get("abilities", []),
            id=str(uuid.uuid4()),
            created_at=datetime.now().isoformat()
        )
        
        return character
    
    async def enhance_character(self, character: Character, world: World, aspect: str) -> Character:
        """
        增强现有角色的特定方面。
        
        Args:
            character: 要增强的角色对象
            world: 角色所属的世界
            aspect: 要增强的方面，例如"背景"、"性格"等
            
        Returns:
            更新后的角色对象
        """
        # 构建提示词
        prompt = self._build_enhancement_prompt(character, world, aspect)
        
        # 调用LLM获取增强内容
        response = await self.llm.generate(prompt)
        
        # 解析LLM响应
        updated_character = self._update_character_aspect(character, aspect, response)
        
        return updated_character
    
    def _build_character_prompt(self, world: World, description: str) -> str:
        """
        构建创建角色的提示词。
        
        Args:
            world: 角色所属的世界
            description: 角色的基本描述
            
        Returns:
            完整的提示词
        """
        world_summary = world.get_summary()
        
        return f"""你是一个专业的中文小说角色设计师，请根据以下世界观和角色描述创建一个详细、立体且有创意的角色。请提供JSON格式的回答。

世界观概要：
{world_summary}

角色描述：
{description}

请包含以下内容：
1. 角色名称(name)：为这个角色取一个符合世界观的名字
2. 基本信息(basic_info)：包含年龄、性别、种族、职业等基本信息，以JSON对象形式提供
3. 外貌(appearance)：角色的外表描述
4. 性格(personality)：角色的性格特点和行为模式
5. 背景(background)：角色的成长经历和过去的故事
6. 能力(abilities)：角色的特殊能力或技能，以数组形式提供

请以JSON格式回答，使用中文，确保内容既有创意又与世界观和用户描述一致。角色应该具有深度和复杂性，同时保持内在的一致性。"""
    
    def _build_enhancement_prompt(self, character: Character, world: World, aspect: str) -> str:
        """
        构建增强角色特定方面的提示词。
        
        Args:
            character: 要增强的角色对象
            world: 角色所属的世界
            aspect: 要增强的方面
            
        Returns:
            完整的提示词
        """
        character_summary = character.get_summary()
        world_summary = world.get_summary()
        
        return f"""你是一个专业的中文小说角色设计师，请为现有角色增强"{aspect}"方面的内容。请提供JSON格式的回答。

世界观概要：
{world_summary}

当前角色概要：
{character_summary}

请详细增强角色的"{aspect}"内容，使其更加丰富、具体和有创意。内容应与现有角色设定和世界观保持一致，同时增加深度和细节。

请以JSON格式回答，键名为"{aspect}"，值为增强后的内容。使用中文，确保内容既有创意又与现有角色设定和世界观一致。"""
    
    def _parse_character_response(self, response: str, description: str) -> Dict[str, Any]:
        """
        解析LLM的角色创建响应。
        
        Args:
            response: LLM的响应文本
            description: 原始角色描述，用于回退
            
        Returns:
            解析后的角色数据
        """
        try:
            # 尝试从响应中提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                character_data = json.loads(json_str)
                return character_data
            else:
                # 如果没有找到JSON，使用默认结构
                return {
                    "name": "未命名角色",
                    "basic_info": {},
                    "background": description
                }
        except json.JSONDecodeError:
            # JSON解析失败，使用默认结构
            return {
                "name": "未命名角色",
                "basic_info": {},
                "background": description
            }
    
    def _update_character_aspect(self, character: Character, aspect: str, response: str) -> Character:
        """
        根据LLM响应更新角色的特定方面。
        
        Args:
            character: 要更新的角色对象
            aspect: 更新的方面
            response: LLM的响应
            
        Returns:
            更新后的角色对象
        """
        try:
            # 尝试从响应中提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                update_data = json.loads(json_str)
                
                # 映射aspect到character的属性
                aspect_mapping = {
                    "基本信息": "basic_info",
                    "外貌": "appearance",
                    "性格": "personality",
                    "背景": "background",
                    "能力": "abilities"
                }
                
                # 更新对应的属性
                english_aspect = aspect_mapping.get(aspect, aspect)
                if english_aspect in update_data:
                    setattr(character, english_aspect, update_data[english_aspect])
                elif aspect in update_data:
                    setattr(character, english_aspect, update_data[aspect])
            
            return character
            
        except (json.JSONDecodeError, AttributeError):
            # 解析失败，返回原始角色对象
            return character 