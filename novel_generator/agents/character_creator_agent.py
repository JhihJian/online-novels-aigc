"""
角色创建代理模块，用于与LLM交互生成角色。
整合了agno库的Agent功能实现更高效的交互。
"""

import json
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from agno.agent import Agent
from agno.tools import tool

from novel_generator.models.world import World
from novel_generator.models.character import Character
from novel_generator.llm.base import BaseLLM


class CharacterCreatorAgent(Agent):
    """角色创建代理，负责与LLM交互生成角色，基于agno的Agent实现"""
    
    def __init__(self, llm: BaseLLM):
        """
        初始化角色创建代理。
        
        Args:
            llm: 语言模型接口
        """
        super().__init__(
            name="CharacterCreatorAgent", 
            description="负责创建和扩展小说角色的AI代理"
        )
        self.llm = llm
        self._register_tools()
    
    def _register_tools(self):
        """注册代理可用的工具"""
        
        @tool(description="创建新的角色")
        async def generate_character(world_data: Dict[str, Any], description: str) -> Dict[str, Any]:
            """
            创建新的角色。
            
            Args:
                world_data: 角色所属的世界数据
                description: 角色的基本描述
                
            Returns:
                创建的角色数据
            """
            # 创建World对象
            world = World.from_dict(world_data)
            
            # 构建提示词
            prompt = self._build_character_prompt(world, description)
            
            # 调用LLM获取角色
            response = await self.llm.generate(prompt)
            
            # 解析LLM响应
            character_data = self._parse_character_response(response, description)
            character_data["world_id"] = world.id
            
            return character_data
        
        @tool(description="增强角色的特定方面")
        async def enhance_character_aspect(world_data: Dict[str, Any], character_data: Dict[str, Any], aspect: str) -> Dict[str, Any]:
            """
            增强角色的特定方面。
            
            Args:
                world_data: 角色所属的世界数据
                character_data: 角色数据
                aspect: 要增强的方面
                
            Returns:
                增强后的角色数据
            """
            # 创建World和Character对象
            world = World.from_dict(world_data)
            character = Character.from_dict(character_data)
            
            # 构建提示词
            prompt = self._build_enhancement_prompt(world, character, aspect)
            
            # 调用LLM获取增强内容
            response = await self.llm.generate(prompt)
            
            # 解析LLM响应，更新Character对象
            updated_character = self._update_character_aspect(character, aspect, response)
            
            # 返回更新后的字典
            return updated_character.to_dict()
        
        # 直接设置tools属性
        self.tools = {
            "generate_character": generate_character,
            "enhance_character_aspect": enhance_character_aspect
        }
    
    async def create_character(self, world: World, description: str) -> Character:
        """
        创建新的角色。
        
        Args:
            world: 角色所属的世界
            description: 角色的基本描述
            
        Returns:
            创建的角色对象
        """
        # 获取世界数据
        world_data = world.to_dict()
        
        # 调用代理的generate_character工具
        result = await self.tools["generate_character"](world_data, description)
        
        # 创建角色对象
        character = Character(
            name=result.get("name", "未命名角色"),
            role=result.get("role", ""),
            appearance=result.get("appearance", ""),
            personality=result.get("personality", ""),
            background=result.get("background", ""),
            abilities=result.get("abilities", ""),
            goals=result.get("goals", ""),
            relationships=result.get("relationships", []),
            world_id=world.id,
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
        # 获取角色和世界数据
        character_data = character.to_dict()
        world_data = world.to_dict()
        
        # 调用代理的enhance_character_aspect工具
        result = await self.tools["enhance_character_aspect"](world_data, character_data, aspect)
        
        # 返回更新后的角色对象
        return Character.from_dict(result)
    
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
        
        return f"""你是一个专业的中文小说角色设计师，请根据以下世界观和描述创建一个丰满、立体且有魅力的角色。请提供JSON格式的回答。

世界观概要：
{world_summary}

角色描述：
{description}

请包含以下内容：
1. 角色名称(name)：为这个角色取一个适合世界观的名字
2. 角色定位(role)：角色在故事中的定位或职业
3. 外貌描述(appearance)：角色的外表特征
4. 性格特点(personality)：角色的性格和行为模式
5. 背景故事(background)：角色的成长经历和背景
6. 能力(abilities)：角色的技能、天赋或特殊能力
7. 目标和动机(goals)：角色的追求和行动动机
8. 人际关系(relationships)：与其他角色或势力的关系，以数组形式提供

请以JSON格式回答，使用中文，确保内容既有创意又与世界观和用户描述一致。角色应该具有深度和复杂性，同时保持内在的一致性。"""
    
    def _build_enhancement_prompt(self, world: World, character: Character, aspect: str) -> str:
        """
        构建增强角色特定方面的提示词。
        
        Args:
            world: 角色所属的世界
            character: 要增强的角色对象
            aspect: 要增强的方面
            
        Returns:
            完整的提示词
        """
        world_summary = world.get_summary()
        character_summary = character.get_summary()
        
        return f"""你是一个专业的中文小说角色设计师，请为现有角色的"{aspect}"方面进行深化和扩展。请提供JSON格式的回答。

世界观概要：
{world_summary}

角色当前概要：
{character_summary}

请详细扩展角色的"{aspect}"方面，使其更加丰富、具体和有深度。内容应与角色现有设定和世界观保持一致，同时增加细节和复杂性。

请以JSON格式回答，键名为"{aspect}"，值为扩展后的内容。使用中文，确保内容既有创意又与角色现有设定和世界观一致。"""
    
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
                    "role": "",
                    "appearance": "",
                    "personality": "",
                    "background": description,
                    "abilities": "",
                    "goals": "",
                    "relationships": []
                }
        except json.JSONDecodeError:
            # JSON解析失败，使用默认结构
            return {
                "name": "未命名角色",
                "role": "",
                "appearance": "",
                "personality": "",
                "background": description,
                "abilities": "",
                "goals": "",
                "relationships": []
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
                    "名称": "name",
                    "角色定位": "role",
                    "外貌": "appearance",
                    "性格": "personality",
                    "背景": "background",
                    "能力": "abilities",
                    "目标": "goals",
                    "人际关系": "relationships"
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