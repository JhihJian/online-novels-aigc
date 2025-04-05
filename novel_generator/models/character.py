"""
人物数据模型模块，定义小说人物的结构和属性。
"""

from typing import Dict, List, Any, Optional
import uuid
import datetime


class Character:
    """人物数据模型，描述小说中的角色。"""
    
    def __init__(
        self,
        name: str,
        world_id: str,
        basic_info: Dict[str, Any] = None,
        appearance: str = "",
        personality: List[str] = None,
        background: str = "",
        abilities: Dict[str, Any] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime.datetime] = None,
    ):
        """
        初始化人物对象。
        
        Args:
            name: 人物姓名
            world_id: 所属世界的ID
            basic_info: 基本信息（性别、年龄、种族等）
            appearance: 外貌描述
            personality: 性格特点列表
            background: 背景故事
            abilities: 能力特点
            id: 唯一标识符（可选，默认自动生成）
            created_at: 创建时间（可选，默认当前时间）
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.world_id = world_id
        self.basic_info = basic_info or {}
        self.appearance = appearance
        self.personality = personality or []
        self.background = background
        self.abilities = abilities or {}
        self.created_at = created_at or datetime.datetime.now()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将人物对象转换为字典。
        
        Returns:
            包含所有人物数据的字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "world_id": self.world_id,
            "basic_info": self.basic_info,
            "appearance": self.appearance,
            "personality": self.personality,
            "background": self.background,
            "abilities": self.abilities,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        """
        从字典创建人物对象。
        
        Args:
            data: 包含人物数据的字典
            
        Returns:
            创建的人物对象
        """
        created_at = datetime.datetime.fromisoformat(data.get("created_at")) if "created_at" in data else None
        
        return cls(
            id=data.get("id"),
            name=data["name"],
            world_id=data["world_id"],
            basic_info=data.get("basic_info", {}),
            appearance=data.get("appearance", ""),
            personality=data.get("personality", []),
            background=data.get("background", ""),
            abilities=data.get("abilities", {}),
            created_at=created_at,
        )
    
    def get_summary(self) -> str:
        """
        获取人物摘要。
        
        Returns:
            人物的文本摘要
        """
        # 构建基本信息摘要
        basic_info_text = "\n".join([f"{k}: {v}" for k, v in self.basic_info.items()]) if self.basic_info else "暂无基本信息"
        
        # 构建性格特点摘要
        personality_text = "\n".join([f"- {trait}" for trait in self.personality]) if self.personality else "暂无性格描述"
        
        # 构建能力特点摘要
        abilities_text = ""
        for category, abilities in self.abilities.items():
            abilities_text += f"{category}:\n"
            if isinstance(abilities, dict):
                for name, desc in abilities.items():
                    abilities_text += f"- {name}: {desc}\n"
            elif isinstance(abilities, list):
                for ability in abilities:
                    if isinstance(ability, dict) and "name" in ability:
                        abilities_text += f"- {ability['name']}"
                        if "description" in ability:
                            abilities_text += f": {ability['description']}"
                        abilities_text += "\n"
                    else:
                        abilities_text += f"- {ability}\n"
            else:
                abilities_text += f"- {abilities}\n"
        
        if not abilities_text:
            abilities_text = "暂无能力描述"
        
        return f"""人物名称: {self.name}

【基本信息】
{basic_info_text}

【外貌描述】
{self.appearance or "暂无外貌描述"}

【性格特点】
{personality_text}

【背景故事】
{self.background or "暂无背景故事"}

【能力特点】
{abilities_text}
""" 