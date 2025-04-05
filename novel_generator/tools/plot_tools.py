"""
剧情查询和修改工具模块。
"""

from typing import Dict, Any, List, Optional
import json

from novel_generator.storage.json_storage import JsonStorage
from novel_generator.models.plot import Plot


class PlotTools:
    """剧情工具类，提供查询和修改剧情数据的功能。"""
    
    def __init__(self, storage: JsonStorage):
        """
        初始化剧情工具。
        
        Args:
            storage: 数据存储对象
        """
        self.storage = storage
    
    def query_plot(self, plot_id: str, query_path: str = "") -> Any:
        """
        查询剧情的特定部分。
        
        Args:
            plot_id: 剧情ID
            query_path: 查询路径，用点分隔，例如"chapters.0.title"
            
        Returns:
            查询结果
            
        Raises:
            FileNotFoundError: 找不到剧情
            KeyError: 查询路径无效
        """
        try:
            # 加载剧情数据
            plot_data = self.storage.load("plots", plot_id)
            
            # 如果没有指定查询路径，返回整个剧情
            if not query_path:
                return plot_data
            
            # 解析查询路径
            path_parts = query_path.split(".")
            result = plot_data
            
            # 逐层查询
            for part in path_parts:
                if isinstance(result, dict) and part in result:
                    result = result[part]
                elif isinstance(result, list) and part.isdigit() and int(part) < len(result):
                    result = result[int(part)]
                else:
                    raise KeyError(f"查询路径'{query_path}'无效，'{part}'不存在")
            
            return result
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到ID为'{plot_id}'的剧情")
    
    def update_plot(self, plot_id: str, update_path: str, value: Any) -> Dict[str, Any]:
        """
        更新剧情的特定部分。
        
        Args:
            plot_id: 剧情ID
            update_path: 更新路径，用点分隔，例如"chapters.0.title"
            value: 新值
            
        Returns:
            更新后的剧情数据
            
        Raises:
            FileNotFoundError: 找不到剧情
            KeyError: 更新路径无效
        """
        try:
            # 加载剧情数据
            plot_data = self.storage.load("plots", plot_id)
            
            # 如果没有指定更新路径，替换整个剧情（保留ID和world_id）
            if not update_path:
                if isinstance(value, dict):
                    value["id"] = plot_data["id"]
                    if "world_id" in plot_data:
                        value["world_id"] = plot_data["world_id"]
                    self.storage.save(value, "plots", plot_id)
                    return value
                else:
                    raise ValueError("如果不指定更新路径，新值必须是字典")
            
            # 解析更新路径
            path_parts = update_path.split(".")
            target = plot_data
            
            # 找到倒数第二层
            for part in path_parts[:-1]:
                if isinstance(target, dict) and part in target:
                    target = target[part]
                elif isinstance(target, list) and part.isdigit() and int(part) < len(target):
                    target = target[int(part)]
                else:
                    raise KeyError(f"更新路径'{update_path}'无效，'{part}'不存在")
            
            # 更新最后一层
            last_part = path_parts[-1]
            if isinstance(target, dict):
                target[last_part] = value
            elif isinstance(target, list) and last_part.isdigit() and int(last_part) < len(target):
                target[int(last_part)] = value
            else:
                raise KeyError(f"更新路径'{update_path}'无效，'{last_part}'不存在")
            
            # 保存更新后的数据
            self.storage.save(plot_data, "plots", plot_id)
            
            return plot_data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到ID为'{plot_id}'的剧情")
    
    def get_chapter_outline(self, plot_id: str, chapter_index: int) -> Dict[str, Any]:
        """
        获取特定章节的大纲。
        
        Args:
            plot_id: 剧情ID
            chapter_index: 章节索引（从0开始）
            
        Returns:
            章节大纲数据
            
        Raises:
            FileNotFoundError: 找不到剧情
            IndexError: 章节索引超出范围
        """
        try:
            # 加载剧情数据
            plot_data = self.storage.load("plots", plot_id)
            plot = Plot.from_dict(plot_data)
            
            chapter = plot.get_chapter(chapter_index)
            if not chapter:
                raise IndexError(f"章节索引 {chapter_index} 超出范围")
            
            return chapter
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到ID为'{plot_id}'的剧情")
    
    def get_plot_summary(self, plot_id: str) -> str:
        """
        获取剧情摘要。
        
        Args:
            plot_id: 剧情ID
            
        Returns:
            剧情摘要文本
            
        Raises:
            FileNotFoundError: 找不到剧情
        """
        try:
            # 加载剧情数据
            plot_data = self.storage.load("plots", plot_id)
            plot = Plot.from_dict(plot_data)
            
            return plot.get_summary()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到ID为'{plot_id}'的剧情")
    
    def list_plots(self, world_id: str = None) -> List[Dict[str, Any]]:
        """
        获取所有剧情的列表，可选择按世界ID过滤。
        
        Args:
            world_id: 世界ID，如果提供则只返回该世界的剧情
            
        Returns:
            剧情列表，每个元素包含ID和基本信息
        """
        all_plots = self.storage.list("plots")
        
        if world_id:
            return [plot for plot in all_plots if self._get_world_id(plot["id"]) == world_id]
        
        return all_plots
    
    def _get_world_id(self, plot_id: str) -> Optional[str]:
        """获取剧情所属的世界ID"""
        try:
            plot_data = self.storage.load("plots", plot_id)
            return plot_data.get("world_id")
        except:
            return None
    
    def create_plot(self, plot: Plot) -> Dict[str, Any]:
        """
        创建新的剧情。
        
        Args:
            plot: 剧情对象
            
        Returns:
            创建的剧情数据
        """
        plot_data = plot.to_dict()
        self.storage.save(plot_data, "plots", plot.id)
        return plot_data
    
    def delete_plot(self, plot_id: str) -> bool:
        """
        删除剧情。
        
        Args:
            plot_id: 剧情ID
            
        Returns:
            是否成功删除
        """
        return self.storage.delete("plots", plot_id)
    
    def add_chapter(self, plot_id: str, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加新章节到剧情中。
        
        Args:
            plot_id: 剧情ID
            chapter_data: 章节数据，包含title和summary等
            
        Returns:
            更新后的剧情数据
            
        Raises:
            FileNotFoundError: 找不到剧情
        """
        try:
            # 加载剧情数据
            plot_data = self.storage.load("plots", plot_id)
            
            if "chapters" not in plot_data:
                plot_data["chapters"] = []
            
            # 添加章节
            plot_data["chapters"].append(chapter_data)
            
            # 保存更新后的数据
            self.storage.save(plot_data, "plots", plot_id)
            
            return plot_data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到ID为'{plot_id}'的剧情") 