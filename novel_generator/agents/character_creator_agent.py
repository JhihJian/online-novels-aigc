"""
角色创建代理模块，用于与LLM交互生成角色。
整合了agno库的Agent功能实现更高效的交互。
"""

import json
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import random

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
        # 由于agno库需要自己的模型接口，而我们使用的是自定义的BaseLLM接口
        # 这里我们使用直接调用工具的方式而不是通过Agent.run
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
        
        # 直接调用工具函数
        result = await self._direct_call_tool("generate_character", world_data=world_data, description=description)
        
        # 创建角色对象 - 修改为符合Character类构造函数的参数
        basic_info = {
            "role": result.get("role", ""),
            "goals": result.get("goals", "")
        }
        
        personality = []
        if "personality" in result:
            # 尝试将personality字符串拆分为列表
            if isinstance(result["personality"], str):
                personality = [trait.strip() for trait in result["personality"].split(',')]
            else:
                personality = [result["personality"]]
                
        abilities = {
            "main": result.get("abilities", "")
        }
        
        # 处理人际关系
        if "relationships" in result:
            basic_info["relationships"] = result["relationships"]
        
        character = Character(
            name=result.get("name", "未命名角色"),
            world_id=world.id,
            basic_info=basic_info,
            appearance=result.get("appearance", ""),
            personality=personality,
            background=result.get("background", ""),
            abilities=abilities,
            id=str(uuid.uuid4()),
            created_at=datetime.now()
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
        
        # 直接调用工具函数
        result = await self._direct_call_tool("enhance_character_aspect", 
                                             world_data=world_data, 
                                             character_data=character_data, 
                                             aspect=aspect)
        
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
        
        # 检查是否为随机角色请求
        is_random = "随机生成" in description
        
        random_tips = ""
        if is_random:
            character_types = [
                "天才少年/少女，有独特天赋但心态尚不成熟",
                "战场老兵，身经百战但内心有伤痕", 
                "神秘智者，知识渊博但隐藏秘密",
                "江湖浪客，行侠仗义却不拘小节",
                "世家子弟，有优越条件但内心叛逆",
                "平凡人，在非凡世界中寻找自己的位置",
                "隐世高人，技艺精湛但性格古怪",
                "神秘组织成员，身份隐秘但有特殊使命",
                "叛逆者，反抗既定秩序但有自己的信念",
                "边缘人物，生活在社会夹缝中但有特殊洞察力"
            ]
            random_type = random.choice(character_types)
            random_tips = f"\n\n由于这是随机生成角色的请求，请考虑以下角色类型作为灵感：{random_type}"
        
        return f"""你是一个专业的中文小说角色设计师，请根据以下世界观和描述创建一个丰满、立体且有魅力的角色。请提供JSON格式的回答。

世界观概要：
{world_summary}

角色描述：
{description}{random_tips}

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
                is_random = "随机生成" in description
                default_name = "随机角色" if is_random else "未命名角色"
                default_role = self._generate_random_role() if is_random else ""
                
                return {
                    "name": default_name,
                    "role": default_role,
                    "appearance": self._generate_random_appearance() if is_random else "",
                    "personality": self._generate_random_personality() if is_random else "",
                    "background": description,
                    "abilities": self._generate_random_abilities() if is_random else "",
                    "goals": self._generate_random_goals() if is_random else "",
                    "relationships": []
                }
        except json.JSONDecodeError:
            # JSON解析失败，使用默认结构
            is_random = "随机生成" in description
            default_name = "随机角色" if is_random else "未命名角色"
            default_role = self._generate_random_role() if is_random else ""
            
            return {
                "name": default_name,
                "role": default_role,
                "appearance": self._generate_random_appearance() if is_random else "",
                "personality": self._generate_random_personality() if is_random else "",
                "background": description,
                "abilities": self._generate_random_abilities() if is_random else "",
                "goals": self._generate_random_goals() if is_random else "",
                "relationships": []
            }
    
    def _generate_random_role(self) -> str:
        """生成随机角色定位"""
        roles = [
            "神秘的流浪者", "隐世的武学大师", "天才炼丹师", "修仙门派弟子",
            "江湖侠客", "世家继承人", "落魄公子", "奇遇少年/少女", 
            "世外高人", "神秘组织成员"
        ]
        return random.choice(roles)
        
    def _generate_random_appearance(self) -> str:
        """生成随机外貌描述"""
        appearances = [
            "面容清秀，眼神中透露出不同于常人的灵气，一头乌黑的长发随意束起。",
            "身材挺拔，面容坚毅，眉宇间有一道伤疤，彰显着不凡的经历。",
            "相貌平凡，但举手投足间透露出超脱尘世的气质，令人难以忽视。",
            "容貌俊美，衣着华丽，一副世家子弟的打扮，举止优雅从容。",
            "身材矮小但极为灵活，脸上常带着狡黠的笑容，眼神中透露着机敏。"
        ]
        return random.choice(appearances)
        
    def _generate_random_personality(self) -> str:
        """生成随机性格特点"""
        personalities = [
            "性格刚毅坚定，遇事冷静，但对亲近之人极为温和。",
            "活泼开朗，乐观向上，但在重要关头能展现出超乎寻常的智慧和勇气。",
            "深沉内敛，不善言辞，但处事果断，有自己的行事准则。",
            "聪明机智，善于察言观色，但也有孤傲的一面，不愿轻易与人交心。",
            "天真烂漫，心地纯净，对世界充满好奇，却也因此常陷入危险。"
        ]
        return random.choice(personalities)
        
    def _generate_random_abilities(self) -> str:
        """生成随机能力特点"""
        abilities = [
            "拥有罕见的灵气感知能力，能够在修炼中事半功倍。",
            "身怀绝世武功，招式精妙，出手迅捷如风。",
            "精通各种奇门阵法，能布置强大的防御和攻击阵法。",
            "天生异能，能与自然元素沟通，引导自然之力为己所用。",
            "医术高超，能治疗常人难以治愈的伤病，炼制神奇丹药。"
        ]
        return abilities
        
    def _generate_random_goals(self) -> str:
        """生成随机目标和动机"""
        goals = [
            "寻找失落已久的家族秘宝，恢复家族荣光。",
            "追寻更高深的修炼境界，突破自身极限。",
            "为过去的恩人或家人复仇，追查真相。",
            "探索世界的奥秘，寻找传说中的神器或秘境。",
            "保护弱小，匡扶正义，成为人人敬仰的大侠。"
        ]
        return random.choice(goals)
    
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
                    "角色定位": "basic_info.role",
                    "外貌": "appearance",
                    "性格": "personality",
                    "背景": "background",
                    "能力": "abilities.main",
                    "目标": "basic_info.goals",
                    "人际关系": "basic_info.relationships"
                }
                
                # 更新对应的属性
                english_aspect = aspect_mapping.get(aspect, aspect)
                
                if "." in english_aspect:
                    # 处理嵌套字段，如basic_info.role
                    main_field, sub_field = english_aspect.split(".", 1)
                    if main_field == "basic_info":
                        if not hasattr(character, "basic_info") or character.basic_info is None:
                            character.basic_info = {}
                        
                        if aspect in update_data:
                            character.basic_info[sub_field] = update_data[aspect]
                        elif english_aspect.split(".")[-1] in update_data:
                            character.basic_info[sub_field] = update_data[english_aspect.split(".")[-1]]
                    elif main_field == "abilities":
                        if not hasattr(character, "abilities") or character.abilities is None:
                            character.abilities = {}
                        
                        if aspect in update_data:
                            character.abilities[sub_field] = update_data[aspect]
                        elif english_aspect.split(".")[-1] in update_data:
                            character.abilities[sub_field] = update_data[english_aspect.split(".")[-1]]
                else:
                    # 处理直接字段
                    if english_aspect in update_data:
                        # 特殊处理personality字段，确保它是列表
                        if english_aspect == "personality":
                            if isinstance(update_data[english_aspect], str):
                                setattr(character, english_aspect, [trait.strip() for trait in update_data[english_aspect].split(',')])
                            elif isinstance(update_data[english_aspect], list):
                                setattr(character, english_aspect, update_data[english_aspect])
                            else:
                                setattr(character, english_aspect, [str(update_data[english_aspect])])
                        else:
                            setattr(character, english_aspect, update_data[english_aspect])
                    elif aspect in update_data:
                        # 特殊处理personality字段，确保它是列表
                        if english_aspect == "personality":
                            if isinstance(update_data[aspect], str):
                                setattr(character, english_aspect, [trait.strip() for trait in update_data[aspect].split(',')])
                            elif isinstance(update_data[aspect], list):
                                setattr(character, english_aspect, update_data[aspect])
                            else:
                                setattr(character, english_aspect, [str(update_data[aspect])])
                        else:
                            setattr(character, english_aspect, update_data[aspect])
            
            return character
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"角色更新失败: {e}")
            # 解析失败，返回原始角色对象
            return character 