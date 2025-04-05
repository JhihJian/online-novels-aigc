"""
世界观查询和修改工具模块。
"""

from typing import Dict, Any, List, Optional
import json

from novel_generator.storage.json_storage import JsonStorage
from novel_generator.models.world import World


class WorldTools:
    """世界观工具类，提供查询和修改世界观数据的功能。"""
    
    def __init__(self, storage: JsonStorage):
        """
        初始化世界观工具。
        
        Args:
            storage: 数据存储对象
        """
        self.storage = storage
    
    def query_world(self, world_id: str, query_path: str = "") -> Any:
        """
        查询世界观的特定部分。
        
        Args:
            world_id: 世界观ID
            query_path: 查询路径，用点分隔，例如"geography.主要大陆"
            
        Returns:
            查询结果
            
        Raises:
            FileNotFoundError: 找不到世界观
            KeyError: 查询路径无效
        """
        try:
            # 加载世界观数据
            world_data = self.storage.load("worlds", world_id)
            
            # 如果没有指定查询路径，返回整个世界观
            if not query_path:
                return world_data
            
            # 解析查询路径
            path_parts = query_path.split(".")
            result = world_data
            
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
            raise FileNotFoundError(f"找不到ID为'{world_id}'的世界观")
    
    def update_world(self, world_id: str, update_path: str, value: Any) -> Dict[str, Any]:
        """
        更新世界观的特定部分。
        
        Args:
            world_id: 世界观ID
            update_path: 更新路径，用点分隔，例如"geography.主要大陆"
            value: 新值
            
        Returns:
            更新后的世界观数据
            
        Raises:
            FileNotFoundError: 找不到世界观
            KeyError: 更新路径无效
        """
        try:
            # 加载世界观数据
            world_data = self.storage.load("worlds", world_id)
            
            # 如果没有指定更新路径，替换整个世界观（保留ID）
            if not update_path:
                if isinstance(value, dict):
                    value["id"] = world_data["id"]
                    self.storage.save(value, "worlds", world_id)
                    return value
                else:
                    raise ValueError("如果不指定更新路径，新值必须是字典")
            
            # 解析更新路径
            path_parts = update_path.split(".")
            target = world_data
            
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
            self.storage.save(world_data, "worlds", world_id)
            
            return world_data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到ID为'{world_id}'的世界观")
    
    def get_world_summary(self, world_id: str) -> str:
        """
        获取世界观摘要。
        
        Args:
            world_id: 世界观ID
            
        Returns:
            世界观摘要文本
            
        Raises:
            FileNotFoundError: 找不到世界观
        """
        try:
            # 加载世界观数据
            world_data = self.storage.load("worlds", world_id)
            world = World.from_dict(world_data)
            
            return world.get_summary()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到ID为'{world_id}'的世界观")
    
    def list_worlds(self) -> List[Dict[str, Any]]:
        """
        获取所有世界观的列表。
        
        Returns:
            世界观列表，每个元素包含ID和基本信息
        """
        return self.storage.list("worlds")
    
    def create_world(self, world: World) -> Dict[str, Any]:
        """
        创建新的世界观。
        
        Args:
            world: 世界观对象
            
        Returns:
            创建的世界观数据
        """
        world_data = world.to_dict()
        self.storage.save(world_data, "worlds", world.id)
        return world_data
    
    def delete_world(self, world_id: str) -> bool:
        """
        删除世界观。
        
        Args:
            world_id: 世界观ID
            
        Returns:
            是否成功删除
        """
        return self.storage.delete("worlds", world_id) 