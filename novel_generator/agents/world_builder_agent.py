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
        # 由于agno库需要自己的模型接口，而我们使用的是自定义的BaseLLM接口
        # 这里我们使用直接调用工具的方式而不是通过Agent.run
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
            try:
                # 输出所使用的模型信息
                print(f"正在使用模型 {self.llm.model_name} 生成世界...")
                
                # 通过回调执行创建操作
                # 构建提示词
                prompt = self._build_world_prompt(description)
                
                # 调用LLM获取世界观
                response = await self.llm.generate(prompt)
                
                # 解析LLM响应
                world_data = self._parse_world_response(response, description)
                
                # 确保世界数据使用正确的字段名
                world_data = self._normalize_world_data(world_data, description)
                
                return world_data
            except ValueError as e:
                # 处理模型弃用错误
                error_msg = str(e)
                if "has been deprecated" in error_msg:
                    print(f"错误: 模型已被弃用: {error_msg}")
                    print("将使用备用方案生成基础世界...")
                    
                    # 创建一个基础世界数据作为备用
                    world_data = {
                        "name": f"{description[:20]}世界",
                        "description": description,
                        "background": "这个世界有着悠久的历史背景...",
                        "history": "这个世界有着悠久的历史...",
                        "natural_laws": ["修炼之道", "世界运行法则"],
                        "cultures": [{"name": "主要文化", "description": "多元文化在这里交融..."}],
                        "regions": [{"name": "主要地区", "description": "地形多样，包括山脉、平原和海洋..."}],
                        "notable_figures": [{"name": "重要人物", "description": "世界的建立者和守护者"}],
                        "magic_systems": [{"name": "灵气修炼体系", "description": "具有独特的灵气修炼体系..."}],
                        "technologies": [{"name": "主流技术", "description": "技术水平适中..."}]
                    }
                    return world_data
                else:
                    # 其他错误直接抛出
                    raise
        
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
    
    def _normalize_world_data(self, world_data: Dict[str, Any], description: str) -> Dict[str, Any]:
        """
        确保世界数据使用正确的字段名，适配World类的构造函数。
        
        Args:
            world_data: 原始世界数据
            description: 世界描述（用于默认值）
            
        Returns:
            规范化后的世界数据
        """
        normalized = {
            "name": world_data.get("name", "未命名世界"),
            "description": world_data.get("description", description),
            "background": world_data.get("background", ""),
            "history": world_data.get("history", ""),
            "natural_laws": world_data.get("natural_laws", []),
            "regions": world_data.get("regions", []),
            "notable_figures": world_data.get("notable_figures", []),
        }
        
        # 处理文化
        if "cultures" in world_data:
            normalized["cultures"] = world_data["cultures"]
        elif "culture" in world_data:
            normalized["cultures"] = [{"name": "主要文化", "description": world_data["culture"]}]
        else:
            normalized["cultures"] = []
            
        # 处理魔法系统
        if "magic_systems" in world_data:
            normalized["magic_systems"] = world_data["magic_systems"]
        elif "magic_system" in world_data:
            normalized["magic_systems"] = [{"name": "主要魔法系统", "description": world_data["magic_system"]}]
        else:
            normalized["magic_systems"] = []
            
        # 处理技术
        if "technologies" in world_data:
            normalized["technologies"] = world_data["technologies"]
        elif "technology" in world_data:
            normalized["technologies"] = [{"name": "主要技术", "description": world_data["technology"]}]
        else:
            normalized["technologies"] = []
            
        # ID和创建时间
        normalized["id"] = world_data.get("id", str(uuid.uuid4()))
        normalized["created_at"] = world_data.get("created_at", datetime.now().isoformat())
        
        return normalized
    
    async def _direct_call_tool(self, tool_name: str, **kwargs):
        """
        直接调用工具函数，绕过Agent.run机制
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            raise ValueError(f"工具 {tool_name} 不存在")
            
        # 获取工具函数
        tool_func = self.tools[tool_name].entrypoint
        
        # 直接调用工具函数
        return await tool_func(**kwargs)
        
    async def create_world(self, description: str) -> World:
        """
        创建新的世界观。
        
        Args:
            description: 世界的基本描述
            
        Returns:
            创建的世界对象
        """
        # 直接调用工具函数
        result = await self._direct_call_tool("generate_world", description=description)
        
        # 创建世界对象 - 修改参数以匹配World类的构造函数
        world = World(
            name=result.get("name", "未命名世界"),
            description=result.get("description", description),
            history=result.get("history", ""),
            background=result.get("background", ""),
            natural_laws=result.get("natural_laws", []),
            cultures=result.get("cultures", [{"name": result.get("culture", "未知文化"), "description": ""}]) if result.get("culture") else [],
            regions=result.get("regions", []),
            notable_figures=result.get("notable_figures", []),
            magic_systems=result.get("magic_systems", [{"name": result.get("magic_system", ""), "description": ""}]) if result.get("magic_system") else [],
            technologies=result.get("technologies", [{"name": result.get("technology", ""), "description": ""}]) if result.get("technology") else [],
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
        
        # 直接调用工具函数
        result = await self._direct_call_tool("extend_world_aspect", world_data=world_data, aspect=aspect)
        
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
3. 背景(background)：世界的整体背景设定
4. 历史(history)：世界的重要历史事件和发展阶段
5. 自然法则(natural_laws)：世界的基本运行规则，以数组形式提供
6. 文化(cultures)：主要文化及其特征，以数组形式提供，每个元素包含name和description
7. 地区(regions)：主要地理区域，以数组形式提供，每个元素包含name和description
8. 重要人物(notable_figures)：世界的重要历史人物，以数组形式提供，每个元素包含name和description
9. 魔法系统(magic_systems)：魔法或特殊力量的规则和限制，以数组形式提供，每个元素包含name和description
10. 技术(technologies)：技术发展水平和特点，以数组形式提供，每个元素包含name和description

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
        
        # 映射中文方面名称到英文字段名
        aspect_mapping = {
            "背景": "background",
            "历史": "history",
            "自然法则": "natural_laws",
            "文化": "cultures",
            "地区": "regions",
            "重要人物": "notable_figures",
            "魔法系统": "magic_systems",
            "技术": "technologies"
        }
        
        english_aspect = aspect_mapping.get(aspect, aspect)
        
        return f"""你是一个专业的中文小说世界观设计师，请对现有世界观的"{aspect}"方面进行扩展和深化。请提供JSON格式的回答。

当前世界观概要：
{world_summary}

请详细扩展"{aspect}"方面的内容，使其更加丰富、具体和有创意。内容应与现有世界观设定保持一致，同时增加深度和细节。

请以JSON格式回答，键名为"{english_aspect}"，值为扩展后的内容。对于数组类型的字段，请提供完整的数组结构，保持每个元素包含name和description属性。

使用中文，确保内容既有创意又与现有世界观设定一致。"""
    
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
                    "background": "",
                    "history": "",
                    "natural_laws": [],
                    "cultures": [],
                    "regions": [],
                    "notable_figures": [],
                    "magic_systems": [],
                    "technologies": []
                }
        except json.JSONDecodeError:
            # JSON解析失败，构建一个最小的世界数据
            return {
                "name": "未命名世界",
                "description": description,
                "background": "",
                "history": "",
                "natural_laws": [],
                "cultures": [],
                "regions": [],
                "notable_figures": [],
                "magic_systems": [],
                "technologies": []
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
                
                # 映射中文方面名称到英文字段名
                aspect_mapping = {
                    "背景": "background",
                    "历史": "history",
                    "自然法则": "natural_laws",
                    "文化": "cultures",
                    "地区": "regions",
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