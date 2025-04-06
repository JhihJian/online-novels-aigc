"""
JSON文件存储模块，提供基于文件系统的JSON数据存储功能。
"""

import os
import json
from typing import Dict, List, Any, Optional


class JsonStorage:
    """JSON文件存储类，用于保存和加载数据到JSON文件。"""
    
    def __init__(self, base_dir: str = "./data"):
        """
        初始化JSON存储对象。
        
        Args:
            base_dir: 数据存储的基础目录
        """
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
        # 创建子目录
        for category in ["worlds", "characters", "plots", "novels"]:
            os.makedirs(os.path.join(base_dir, category), exist_ok=True)
    
    def save(self, data: Dict[str, Any], category: str, id: str) -> str:
        """
        保存数据到JSON文件。
        
        Args:
            data: 要保存的数据字典
            category: 数据类别（worlds, characters, plots, novels）
            id: 数据ID
            
        Returns:
            保存的文件路径
        """
        dir_path = os.path.join(self.base_dir, category)
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, f"{id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def load(self, category: str, id: str) -> Dict[str, Any]:
        """
        从JSON文件加载数据。
        
        Args:
            category: 数据类别（worlds, characters, plots, novels）
            id: 数据ID
            
        Returns:
            加载的数据字典
            
        Raises:
            FileNotFoundError: 如果文件不存在
        """
        file_path = os.path.join(self.base_dir, category, f"{id}.json")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到数据: {category}/{id}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def delete(self, category: str, id: str) -> bool:
        """
        删除JSON文件。
        
        Args:
            category: 数据类别（worlds, characters, plots, novels）
            id: 数据ID
            
        Returns:
            是否成功删除
        """
        file_path = os.path.join(self.base_dir, category, f"{id}.json")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False
    
    def list(self, category: str) -> List[Dict[str, Any]]:
        """
        列出指定类别的所有数据。
        
        Args:
            category: 数据类别（worlds, characters, plots, novels）
            
        Returns:
            数据项列表（每项包含id和基本信息）
        """
        dir_path = os.path.join(self.base_dir, category)
        result = []
        
        if not os.path.exists(dir_path):
            return result
        
        for filename in os.listdir(dir_path):
            if filename.endswith(".json"):
                file_path = os.path.join(dir_path, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # 提取ID和基本信息
                        item = {
                            "id": data.get("id", filename[:-5]),
                            "name": data.get("name", "未命名"),
                            "created_at": data.get("created_at", ""),
                            "updated_at": data.get("updated_at", "")
                        }
                        
                        # 对于角色，添加world_id和basic_info信息
                        if category == "characters":
                            item["world_id"] = data.get("world_id", "")
                            if "basic_info" in data and isinstance(data["basic_info"], dict):
                                item["basic_info"] = data["basic_info"]
                            
                        result.append(item)
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {e}")
        
        # 按创建时间排序（如果有）
        result.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return result 