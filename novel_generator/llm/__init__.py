"""
语言模型接口包，提供与各种LLM交互的标准接口。
"""

from novel_generator.llm.base import BaseLLM
from novel_generator.llm.gemini import GeminiLLM

__all__ = [
    'BaseLLM',
    'GeminiLLM'
] 