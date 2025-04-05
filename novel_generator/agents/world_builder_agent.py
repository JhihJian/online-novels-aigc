"""
世界构建代理模块，用于与LLM交互生成世界观。
整合了agno库的Agent功能实现更高效的交互。
"""

import json
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from agno.agent import Agent
from agno.tools import tool

from novel_generator.models.world import World
from novel_generator.llm.base import BaseLLM


class WorldBuilderAgent(Agent):
    """世界构建代理，负责与LLM交互生成世界观，基于agno的Agent实现"""
    
    def __init__(self, llm: BaseLLM):
        """
        初始化世界构建代理。
        
        Args:
            llm: 语言模型接口
        """
        super().__init__(
            name="WorldBuilderAgent", 
            description="负责创建和扩展小说世界观的AI代理"
        )
        self.llm = llm
        self._register_tools()
    
    def _register_tools(self):
        """注册代理可用的工具"""
        
        @tool(description="创建新的世界观")
        async def generate_world(description: str) -> Dict[str, Any]:
            """
            创建新的世界观。
            
            Args:
                description: 世界的基本描述
                
            Returns:
                创建的世界数据
            """
            # 通过回调执行创建操作
            # 构建提示词
            prompt = self._build_world_prompt(description)
            
            # 调用LLM获取世界观
            response = await self.llm.generate(prompt)
            
            # 解析LLM响应
            world_data = self._parse_world_response(response, description)
            
            # 创建World对象
            world = World(
                name=world_data.get("name", "未命名世界"),
                description=world_data.get("description", description),
                history=world_data.get("history", ""),
                culture=world_data.get("culture", ""),
                geography=world_data.get("geography", ""),
                politics=world_data.get("politics", ""),
                economics=world_data.get("economics", ""),
                magic_system=world_data.get("magic_system", ""),
                technology=world_data.get("technology", ""),
                races=world_data.get("races", []),
                factions=world_data.get("factions", []),
                id=str(uuid.uuid4()),
                created_at=datetime.now().isoformat()
            )
            
            return world_data
        
        @tool(description="扩展世界观的特定方面")
        async def extend_world_aspect(world_data: Dict[str, Any], aspect: str) -> Dict[str, Any]:
            """
            扩展世界观的特定方面。
            
            Args:
                world_data: 世界数据
                aspect: 要扩展的方面
                
            Returns:
                扩展后的世界数据
            """
            # 创建World对象
            world = World.from_dict(world_data)
            
            # 构建提示词
            prompt = self._build_extension_prompt(world, aspect)
            
            # 调用LLM获取扩展内容
            response = await self.llm.generate(prompt)
            
            # 解析LLM响应，更新World对象
            updated_world = self._update_world_aspect(world, aspect, response)
            
            # 返回更新后的字典
            return updated_world.to_dict()
        
        # 直接设置tools属性
        self.tools = {
            "generate_world": generate_world,
            "extend_world_aspect": extend_world_aspect
        }
    
    async def create_world(self, description: str) -> World:
        """
        创建新的世界观。
        
        Args:
            description: 世界的基本描述
            
        Returns:
            创建的世界对象
        """
        # 调用代理的generate_world工具
        result = await self.tools["generate_world"](description)
        
        # 创建世界对象
        world = World(
            name=result.get("name", "未命名世界"),
            description=result.get("description", description),
            history=result.get("history", ""),
            culture=result.get("culture", ""),
            geography=result.get("geography", ""),
            politics=result.get("politics", ""),
            economics=result.get("economics", ""),
            magic_system=result.get("magic_system", ""),
            technology=result.get("technology", ""),
            races=result.get("races", []),
            factions=result.get("factions", []),
            id=str(uuid.uuid4()),
            created_at=datetime.now().isoformat()
        )
        
        return world
    
    async def extend_world(self, world: World, aspect: str) -> World:
        """
        扩展现有世界观的特定方面。
        
        Args:
            world: 要扩展的世界对象
            aspect: 要扩展的方面，例如"历史"、"文化"等
            
        Returns:
            更新后的世界对象
        """
        # 获取世界数据
        world_data = world.to_dict()
        
        # 调用代理的extend_world_aspect工具
        result = await self.tools["extend_world_aspect"](world_data, aspect)
        
        # 返回更新后的世界对象
        return World.from_dict(result)
    
    def _build_world_prompt(self, description: str) -> str:
        """
        构建创建世界观的提示词。
        
        Args:
            description: 世界的基本描述
            
        Returns:
            完整的提示词
        """
        return f"""你是一个专业的中文小说世界观设计师，请根据以下描述创建一个详细、合理且有深度的奇幻/玄幻小说世界观。请提供JSON格式的回答。

描述：
{description}

请包含以下内容：
1. 世界名称(name)：为这个世界取一个富有特色的名称
2. 世界描述(description)：对世界的整体概括
3. 历史(history)：世界的重要历史事件和发展阶段
4. 文化(culture)：主要种族/国家的文化特征
5. 地理(geography)：主要地形、区域和气候特征
6. 政治(politics)：统治体系和主要政治力量
7. 经济(economics)：经济体系和资源分布
8. 魔法/超自然体系(magic_system)：魔法或特殊力量的规则和限制
9. 技术(technology)：技术发展水平和特点
10. 种族(races)：主要种族及其特点，以数组形式提供
11. 势力(factions)：主要势力或组织，以数组形式提供

请以JSON格式回答，使用中文，确保内容既有创意又合理自洽。世界观应该具有内在的一致性和深度，同时充满独特的魅力和探索的可能性。"""
    
    def _build_extension_prompt(self, world: World, aspect: str) -> str:
        """
        构建扩展世界观特定方面的提示词。
        
        Args:
            world: 要扩展的世界对象
            aspect: 要扩展的方面
            
        Returns:
            完整的提示词
        """
        world_summary = world.get_summary()
        
        return f"""你是一个专业的中文小说世界观设计师，请对现有世界观的"{aspect}"方面进行扩展和深化。请提供JSON格式的回答。

当前世界观概要：
{world_summary}

请详细扩展"{aspect}"方面的内容，使其更加丰富、具体和有创意。内容应与现有世界观设定保持一致，同时增加深度和细节。

请以JSON格式回答，键名为"{aspect}"，值为扩展后的内容。使用中文，确保内容既有创意又与现有世界观设定一致。"""
    
    def _parse_world_response(self, response: str, description: str) -> Dict[str, Any]:
        """
        解析LLM的世界观创建响应。
        
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
                # 如果没有找到JSON，构建一个最小的世界数据
                return {
                    "name": "未命名世界",
                    "description": description,
                    "history": "",
                    "culture": "",
                    "geography": "",
                    "politics": "",
                    "economics": "",
                    "magic_system": "",
                    "technology": "",
                    "races": [],
                    "factions": []
                }
        except json.JSONDecodeError:
            # JSON解析失败，构建一个最小的世界数据
            return {
                "name": "未命名世界",
                "description": description,
                "history": "",
                "culture": "",
                "geography": "",
                "politics": "",
                "economics": "",
                "magic_system": "",
                "technology": "",
                "races": [],
                "factions": []
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
                    "历史": "history",
                    "文化": "culture",
                    "地理": "geography",
                    "政治": "politics",
                    "经济": "economics",
                    "魔法体系": "magic_system",
                    "技术": "technology",
                    "种族": "races",
                    "势力": "factions"
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