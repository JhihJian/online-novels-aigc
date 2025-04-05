"""
剧情数据模型模块，定义小说剧情的结构和属性。
"""

from typing import Dict, List, Any, Optional
import uuid
import datetime


class Plot:
    """剧情数据模型，描述小说的剧情大纲。"""
    
    def __init__(
        self,
        title: str,
        world_id: str,
        background: str = "",
        main_plot: Dict[str, Any] = None,
        turning_points: List[Dict[str, Any]] = None,
        chapters: List[Dict[str, Any]] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime.datetime] = None,
    ):
        """
        初始化剧情对象。
        
        Args:
            title: 故事标题
            world_id: 所属世界的ID
            background: 故事背景
            main_plot: 主线剧情
            turning_points: 转折点列表
            chapters: 章节概要列表
            id: 唯一标识符（可选，默认自动生成）
            created_at: 创建时间（可选，默认当前时间）
        """
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.world_id = world_id
        self.background = background
        self.main_plot = main_plot or {}
        self.turning_points = turning_points or []
        self.chapters = chapters or []
        self.created_at = created_at or datetime.datetime.now()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将剧情对象转换为字典。
        
        Returns:
            包含所有剧情数据的字典
        """
        return {
            "id": self.id,
            "title": self.title,
            "world_id": self.world_id,
            "background": self.background,
            "main_plot": self.main_plot,
            "turning_points": self.turning_points,
            "chapters": self.chapters,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Plot":
        """
        从字典创建剧情对象。
        
        Args:
            data: 包含剧情数据的字典
            
        Returns:
            创建的剧情对象
        """
        created_at = datetime.datetime.fromisoformat(data.get("created_at")) if "created_at" in data else None
        
        return cls(
            id=data.get("id"),
            title=data["title"],
            world_id=data["world_id"],
            background=data.get("background", ""),
            main_plot=data.get("main_plot", {}),
            turning_points=data.get("turning_points", []),
            chapters=data.get("chapters", []),
            created_at=created_at,
        )
    
    def get_summary(self) -> str:
        """
        获取剧情摘要。
        
        Returns:
            剧情的文本摘要
        """
        # 构建主线剧情摘要
        main_plot_text = ""
        if self.main_plot:
            if isinstance(self.main_plot, dict):
                for key, value in self.main_plot.items():
                    main_plot_text += f"{key}: {value}\n"
            else:
                main_plot_text = str(self.main_plot)
        
        if not main_plot_text:
            main_plot_text = "暂无主线剧情"
        
        # 构建转折点摘要
        turning_points_text = ""
        for i, tp in enumerate(self.turning_points, 1):
            if isinstance(tp, dict):
                name = tp.get("name", f"转折点{i}")
                description = tp.get("description", "")
                turning_points_text += f"{i}. {name}: {description}\n"
            else:
                turning_points_text += f"{i}. {tp}\n"
        
        if not turning_points_text:
            turning_points_text = "暂无转折点"
        
        # 构建章节概要摘要
        chapters_text = ""
        for i, chapter in enumerate(self.chapters, 1):
            if isinstance(chapter, dict):
                title = chapter.get("title", f"第{i}章")
                summary = chapter.get("summary", "")
                chapters_text += f"第{i}章 - {title}: {summary}\n\n"
            else:
                chapters_text += f"第{i}章: {chapter}\n\n"
        
        if not chapters_text:
            chapters_text = "暂无章节概要"
        
        return f"""故事标题: {self.title}

【故事背景】
{self.background or "暂无故事背景"}

【主线剧情】
{main_plot_text}

【关键转折点】
{turning_points_text}

【章节概要】
{chapters_text}
"""
    
    def get_chapter(self, index: int) -> Optional[Dict[str, Any]]:
        """
        获取指定章节的数据。
        
        Args:
            index: 章节索引（从0开始）
            
        Returns:
            章节数据，如果索引无效则返回None
        """
        if 0 <= index < len(self.chapters):
            return self.chapters[index]
        return None 