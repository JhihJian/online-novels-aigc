"""
人物查询和修改工具模块。
"""

from typing import Dict, Any, List, Optional
import json

from novel_generator.storage.json_storage import JsonStorage
from novel_generator.models.character import Character


class CharacterTools:
    """人物工具类，提供查询和修改人物数据的功能。"""
    
    def __init__(self, storage: JsonStorage):
        """
        初始化人物工具。
        
        Args:
            storage: 数据存储对象
        """
        self.storage = storage
    
    def query_character(self, character_id: str, query_path: str = "") -> Any:
        """
        查询人物的特定属性。
        
        Args:
            character_id: 人物ID
            query_path: 查询路径，用点分隔，例如"basic_info.年龄"
            
        Returns:
            查询结果
            
        Raises:
            FileNotFoundError: 找不到人物
            KeyError: 查询路径无效
        """
        try:
            # 加载人物数据
            char_data = self.storage.load("characters", character_id)
            
            # 如果没有指定查询路径，返回整个人物数据
            if not query_path:
                return char_data
            
            # 解析查询路径
            path_parts = query_path.split(".")
            result = char_data
            
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
            raise FileNotFoundError(f"找不到ID为'{character_id}'的人物")
    
    def update_character(self, character_id: str, update_path: str, value: Any) -> Dict[str, Any]:
        """
        更新人物的特定属性。
        
        Args:
            character_id: 人物ID
            update_path: 更新路径，用点分隔，例如"basic_info.年龄"
            value: 新值
            
        Returns:
            更新后的人物数据
            
        Raises:
            FileNotFoundError: 找不到人物
            KeyError: 更新路径无效
        """
        try:
            # 加载人物数据
            char_data = self.storage.load("characters", character_id)
            
            # 如果没有指定更新路径，替换整个人物数据（保留ID和world_id）
            if not update_path:
                if isinstance(value, dict):
                    value["id"] = char_data["id"]
                    if "world_id" in char_data:
                        value["world_id"] = char_data["world_id"]
                    self.storage.save(value, "characters", character_id)
                    return value
                else:
                    raise ValueError("如果不指定更新路径，新值必须是字典")
            
            # 解析更新路径
            path_parts = update_path.split(".")
            target = char_data
            
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
            self.storage.save(char_data, "characters", character_id)
            
            return char_data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到ID为'{character_id}'的人物")
    
    def get_character_summary(self, character_id: str) -> str:
        """
        获取人物摘要。
        
        Args:
            character_id: 人物ID
            
        Returns:
            人物摘要文本
            
        Raises:
            FileNotFoundError: 找不到人物
        """
        try:
            # 加载人物数据
            char_data = self.storage.load("characters", character_id)
            character = Character.from_dict(char_data)
            
            return character.get_summary()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到ID为'{character_id}'的人物")
    
    def list_characters(self, world_id: str = None) -> List[Dict[str, Any]]:
        """
        获取人物列表，可选择按世界ID过滤。
        
        Args:
            world_id: 世界ID，如果提供则只返回该世界的人物
            
        Returns:
            人物列表，每个元素包含ID和基本信息
        """
        all_characters = self.storage.list("characters")
        
        if world_id:
            return [char for char in all_characters if self._get_world_id(char["id"]) == world_id]
        
        return all_characters
    
    def _get_world_id(self, character_id: str) -> Optional[str]:
        """获取人物所属的世界ID"""
        try:
            char_data = self.storage.load("characters", character_id)
            return char_data.get("world_id")
        except:
            return None
    
    def create_character(self, character: Character) -> Dict[str, Any]:
        """
        创建新的人物。
        
        Args:
            character: 人物对象
            
        Returns:
            创建的人物数据
        """
        char_data = character.to_dict()
        self.storage.save(char_data, "characters", character.id)
        return char_data
    
    def delete_character(self, character_id: str) -> bool:
        """
        删除人物。
        
        Args:
            character_id: 人物ID
            
        Returns:
            是否成功删除
        """
        return self.storage.delete("characters", character_id) 