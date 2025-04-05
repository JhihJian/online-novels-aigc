"""
语言模型基类模块，定义与LLM交互的标准接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


class BaseLLM(ABC):
    """语言模型基类，定义所有LLM实现必须遵循的接口"""
    
    @abstractmethod
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = None) -> str:
        """
        生成文本响应。
        
        Args:
            prompt: 提示词
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成令牌数，如果为None则使用模型默认值
            
        Returns:
            生成的文本响应
        """
        pass
    
    @abstractmethod
    async def generate_with_history(self, 
                                   messages: List[Dict[str, str]], 
                                   temperature: float = 0.7, 
                                   max_tokens: int = None) -> str:
        """
        基于对话历史生成文本响应。
        
        Args:
            messages: 对话历史，格式为[{"role": "user"|"assistant", "content": "消息内容"}, ...]
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成令牌数，如果为None则使用模型默认值
            
        Returns:
            生成的文本响应
        """
        pass
    
    @abstractmethod
    async def embed(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        获取文本的向量嵌入表示。
        
        Args:
            text: 需要嵌入的文本或文本列表
            
        Returns:
            文本的向量嵌入表示，单个文本返回一维向量，文本列表返回二维向量列表
        """
        pass 