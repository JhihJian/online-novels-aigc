"""
世界观构建代理，负责根据用户描述创建详细的世界观设定。
"""

import json
from typing import Dict, Any

from agno import Agent
from agno.models import Gemini
from novel_generator.models.world import World


class WorldBuilderAgent(Agent):
    """世界观构建代理类，使用Gemini API构建详细的世界观设定。"""
    
    def __init__(self, api_key: str, temperature: float = 0.7, top_p: float = 0.9):
        """
        初始化世界观构建代理。
        
        Args:
            api_key: Gemini API密钥
            temperature: 生成文本的创意度，范围0.0-1.0
            top_p: 生成文本的多样性，范围0.0-1.0
        """
        self.model = Gemini(api_key=api_key, id="gemini-2.0-flash-exp")
        self.temperature = temperature
        self.top_p = top_p
    
    async def create_world(self, description: str) -> World:
        """
        根据用户描述创建详细的世界观。
        
        Args:
            description: 用户提供的世界观描述
            
        Returns:
            创建的世界观对象
        """
        prompt = self._create_world_prompt(description)
        response = await self.model.generate(prompt, temperature=self.temperature, top_p=self.top_p)
        
        # 提取JSON数据
        try:
            json_str = self._extract_json(response)
            world_data = json.loads(json_str)
            
            # 确保必要字段存在
            if "name" not in world_data:
                world_data["name"] = "未命名世界"
            
            return World.from_dict(world_data)
        except Exception as e:
            # 如果JSON解析失败，创建一个基本的世界观
            print(f"解析响应时出错: {e}")
            return World(
                name="解析错误的世界",
                geography={"解析错误": "无法从API响应中提取有效数据"},
                history={"错误描述": str(e)},
                factions=[],
                power_system={},
                culture={}
            )
    
    def _create_world_prompt(self, description: str) -> str:
        """
        创建世界观生成的提示词。
        
        Args:
            description: 用户提供的世界观描述
            
        Returns:
            完整的提示词文本
        """
        return f"""你是一个专业的世界观构建专家，擅长为中文网络小说创建丰富详实的世界设定。
基于用户提供的描述 "{description}"，构建一个完整的世界观，包括：

1. 地理环境（大陆、国家、重要地点）
2. 历史背景（重大历史事件、历史变迁）
3. 种族/势力划分（主要种族、组织、国家、宗派）
4. 力量体系（修炼体系、魔法系统、科技水平）
5. 文化特色（习俗、禁忌、信仰、节日）

你的回答必须是一个结构化的JSON数据，格式如下：

```json
{{
  "name": "世界名称",
  "geography": {{
    "概述": "地理环境总体描述",
    "主要大陆": [
      {{
        "name": "大陆名称",
        "描述": "大陆描述",
        "主要国家/地区": [
          {{
            "name": "国家/地区名称",
            "描述": "国家/地区描述",
            "首都/重要城市": ["城市1", "城市2"]
          }}
        ]
      }}
    ],
    "重要地形": [
      {{
        "name": "地形名称",
        "描述": "地形描述",
        "特殊之处": "特殊性质"
      }}
    ]
  }},
  "history": {{
    "概述": "历史总体描述",
    "重大事件": [
      {{
        "name": "事件名称",
        "时间": "发生时间",
        "描述": "事件描述",
        "影响": "事件影响"
      }}
    ],
    "历史时期": [
      {{
        "name": "时期名称",
        "起止时间": "起止时间",
        "特点": "时期特点",
        "重要人物": ["人物1", "人物2"]
      }}
    ]
  }},
  "factions": [
    {{
      "name": "势力/种族名称",
      "类型": "势力/种族类型",
      "描述": "势力/种族描述",
      "特点": "势力/种族特点",
      "地位": "在世界中的地位",
      "代表人物": ["人物1", "人物2"]
    }}
  ],
  "power_system": {{
    "概述": "力量体系总体描述",
    "类型": [
      {{
        "name": "力量类型名称",
        "描述": "力量类型描述",
        "等级": ["等级1", "等级2", "等级3"],
        "获取方式": "如何获得这种力量",
        "限制": "力量的局限性"
      }}
    ],
    "稀有力量": [
      {{
        "name": "稀有力量名称",
        "描述": "稀有力量描述",
        "持有者": ["持有者1", "持有者2"]
      }}
    ]
  }},
  "culture": {{
    "主流文化": [
      {{
        "name": "文化名称",
        "地域": "文化分布区域",
        "特点": "文化特点",
        "风俗习惯": ["习俗1", "习俗2"],
        "禁忌": ["禁忌1", "禁忌2"]
      }}
    ],
    "宗教信仰": [
      {{
        "name": "宗教名称",
        "信仰内容": "信仰描述",
        "影响范围": "影响区域",
        "重要仪式": ["仪式1", "仪式2"]
      }}
    ],
    "节日": [
      {{
        "name": "节日名称",
        "时间": "举办时间",
        "起源": "节日起源",
        "庆祝方式": "庆祝活动描述"
      }}
    ]
  }}
}}
```

确保生成的JSON数据符合上述格式，并且内容丰富、具有创造性和内部一致性。尽量避免使用过于宽泛和模糊的描述，应提供具体而富有特色的世界观元素。
"""
    
    def _extract_json(self, text: str) -> str:
        """
        从文本中提取JSON字符串。
        
        Args:
            text: 包含JSON的文本
            
        Returns:
            提取出的JSON字符串
        """
        # 尝试查找JSON开始和结束的位置
        start_pos = text.find("{")
        if start_pos == -1:
            raise ValueError("无法在响应中找到JSON开始标记")
        
        # 计算匹配的大括号
        brace_count = 0
        json_end = start_pos
        
        for i in range(start_pos, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                
            if brace_count == 0:
                json_end = i + 1
                break
        
        if brace_count != 0:
            raise ValueError("JSON格式不完整，括号不匹配")
        
        return text[start_pos:json_end] 