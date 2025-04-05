"""
世界模型模块，定义世界的结构和属性。
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class World:
    """世界模型，定义了一个小说世界的结构和属性"""
    
    def __init__(
        self,
        name: str,
        description: str,
        background: str = "",
        natural_laws: List[str] = None,
        cultures: List[Dict[str, Any]] = None,
        history: str = "",
        regions: List[Dict[str, Any]] = None,
        notable_figures: List[Dict[str, str]] = None,
        magic_systems: List[Dict[str, Any]] = None,
        technologies: List[Dict[str, Any]] = None,
        id: str = None,
        created_at: str = None
    ):
        """
        初始化世界模型。
        
        Args:
            name: 世界名称
            description: 世界简要描述
            background: 世界背景详情
            natural_laws: 自然法则列表
            cultures: 文化列表
            history: 世界历史
            regions: 地域列表
            notable_figures: 重要人物列表
            magic_systems: 魔法系统列表
            technologies: 技术列表
            id: 世界ID，如果为None则自动生成
            created_at: 创建时间戳，如果为None则使用当前时间
        """
        self.name = name
        self.description = description
        self.background = background
        self.natural_laws = natural_laws or []
        self.cultures = cultures or []
        self.history = history
        self.regions = regions or []
        self.notable_figures = notable_figures or []
        self.magic_systems = magic_systems or []
        self.technologies = technologies or []
        self.id = id
        self.created_at = created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将世界对象转换为字典。
        
        Returns:
            表示世界的字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "background": self.background,
            "natural_laws": self.natural_laws,
            "cultures": self.cultures,
            "history": self.history,
            "regions": self.regions,
            "notable_figures": self.notable_figures,
            "magic_systems": self.magic_systems,
            "technologies": self.technologies,
            "id": self.id,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'World':
        """
        从字典创建世界对象。
        
        Args:
            data: 表示世界的字典
            
        Returns:
            创建的世界对象
        """
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            background=data.get("background", ""),
            natural_laws=data.get("natural_laws", []),
            cultures=data.get("cultures", []),
            history=data.get("history", ""),
            regions=data.get("regions", []),
            notable_figures=data.get("notable_figures", []),
            magic_systems=data.get("magic_systems", []),
            technologies=data.get("technologies", []),
            id=data.get("id"),
            created_at=data.get("created_at")
        )
    
    def get_summary(self) -> str:
        """
        获取世界的摘要描述。
        
        Returns:
            世界的摘要描述
        """
        summary = f"世界名称：{self.name}\n"
        summary += f"简介：{self.description}\n\n"
        
        if self.background:
            summary += f"背景：{self.background[:200]}...\n\n"
        
        if self.natural_laws:
            summary += "自然法则：\n"
            for i, law in enumerate(self.natural_laws[:3]):
                if isinstance(law, str):
                    summary += f"- {law}\n"
                elif isinstance(law, dict) and "name" in law:
                    summary += f"- {law['name']}\n"
            if len(self.natural_laws) > 3:
                summary += f"  (共{len(self.natural_laws)}条)\n"
            summary += "\n"
        
        if self.cultures:
            summary += "文化：\n"
            for i, culture in enumerate(self.cultures[:3]):
                if isinstance(culture, dict) and "name" in culture:
                    summary += f"- {culture['name']}\n"
                else:
                    summary += f"- 文化{i+1}\n"
            if len(self.cultures) > 3:
                summary += f"  (共{len(self.cultures)}种文化)\n"
            summary += "\n"
        
        if self.regions:
            summary += "地域：\n"
            for i, region in enumerate(self.regions[:3]):
                if isinstance(region, dict) and "name" in region:
                    summary += f"- {region['name']}\n"
                else:
                    summary += f"- 地域{i+1}\n"
            if len(self.regions) > 3:
                summary += f"  (共{len(self.regions)}个地域)\n"
            summary += "\n"
        
        if self.magic_systems:
            summary += "魔法系统：\n"
            for i, magic in enumerate(self.magic_systems[:2]):
                if isinstance(magic, dict) and "name" in magic:
                    summary += f"- {magic['name']}\n"
                else:
                    summary += f"- 魔法系统{i+1}\n"
            if len(self.magic_systems) > 2:
                summary += f"  (共{len(self.magic_systems)}个魔法系统)\n"
            summary += "\n"
        
        if self.technologies:
            summary += "技术：\n"
            for i, tech in enumerate(self.technologies[:2]):
                if isinstance(tech, dict) and "name" in tech:
                    summary += f"- {tech['name']}\n"
                else:
                    summary += f"- 技术{i+1}\n"
            if len(self.technologies) > 2:
                summary += f"  (共{len(self.technologies)}种技术)\n"
        
        return summary 