"""
Google Gemini语言模型实现模块。
"""

import json
import os
import asyncio
from typing import Dict, Any, List, Optional, Union

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from novel_generator.llm.base import BaseLLM


class GeminiLLM(BaseLLM):
    """Google Gemini语言模型实现"""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-pro", generation_config: Dict[str, Any] = None):
        """
        初始化Gemini LLM。
        
        Args:
            api_key: Gemini API密钥，如不提供则从环境变量GEMINI_API_KEY获取
            model_name: 使用的模型名称，默认为"gemini-1.5-pro" (注：旧模型"gemini-pro"可能已不可用)
            generation_config: 生成配置参数
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("必须提供Gemini API密钥，或在环境变量GEMINI_API_KEY中设置")
        
        # 配置API
        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"配置Gemini API时出错: {str(e)}")
        
        # 检查可用模型
        try:
            available_models = [m.name for m in genai.list_models()]
            print(f"可用模型: {available_models}")
            
            # 自动选择可用的gemini模型
            self.model_name = model_name
            if self.model_name not in available_models:
                # 尝试查找可用的gemini模型
                gemini_models = [m for m in available_models if "gemini" in m.lower()]
                if gemini_models:
                    self.model_name = gemini_models[0]
                    print(f"自动选择可用模型: {self.model_name}")
                else:
                    raise ValueError(f"找不到可用的Gemini模型。可用模型: {available_models}")
        except Exception as e:
            print(f"获取模型列表时出错: {str(e)}")
            # 继续使用用户指定的模型，但可能会在后续调用中失败
            self.model_name = model_name
        
        try:
            self.model = genai.GenerativeModel(model_name=self.model_name)
        except Exception as e:
            raise ValueError(f"创建Gemini生成模型时出错: {str(e)}")
        
        # 设置默认生成配置
        self.default_generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
        
        # 使用用户提供的配置覆盖默认配置
        if generation_config:
            self.default_generation_config.update(generation_config)
        
        # 安全设置
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
    
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
        # 准备生成配置
        generation_config = self.default_generation_config.copy()
        generation_config["temperature"] = temperature
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        # 使用同步API并在事件循环中运行
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings=self.safety_settings,
                )
            )
            
            # 提取文本响应
            try:
                return response.text
            except Exception as e:
                # 处理可能的安全过滤或其他错误
                if hasattr(response, 'prompt_feedback'):
                    if response.prompt_feedback.block_reason:
                        raise ValueError(f"提示词被安全过滤拦截: {response.prompt_feedback.block_reason}")
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                        raise ValueError(f"生成被中断: {candidate.finish_reason}")
                raise ValueError(f"生成失败: {str(e)}")
                
        except Exception as e:
            error_msg = str(e)
            if "models/gemini-pro is not found" in error_msg:
                raise ValueError(f"找不到模型 '{self.model_name}'。请尝试更新模型名称，例如 'gemini-1.5-pro'。详细错误: {error_msg}")
            elif "API key not valid" in error_msg:
                raise ValueError(f"API密钥无效。请检查您的API密钥设置。详细错误: {error_msg}")
            else:
                raise ValueError(f"调用Gemini API时出错: {error_msg}")
    
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
        # 准备生成配置
        generation_config = self.default_generation_config.copy()
        generation_config["temperature"] = temperature
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        # 将messages转换为genai的chat格式
        try:
            chat = self.model.start_chat(history=[])
            
            # 添加历史消息
            for message in messages[:-1]:  # 不包括最后一条
                role = message.get("role")
                content = message.get("content", "")
                
                if role == "user":
                    # 模拟用户消息
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None,
                        lambda: chat.send_message(content, stream=False)
                    )
                elif role == "assistant":
                    # 因为无法直接添加助手消息，我们在内部记录中添加
                    chat._history.append({"role": "model", "parts": [content]})
            
            # 发送最后一条用户消息并获取响应
            last_message = messages[-1]
            if last_message.get("role") == "user":
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: chat.send_message(
                        last_message.get("content", ""),
                        generation_config=generation_config,
                        safety_settings=self.safety_settings,
                        stream=False
                    )
                )
                
                # 提取文本响应
                try:
                    return response.text
                except Exception as e:
                    # 处理可能的安全过滤或其他错误
                    if hasattr(response, 'prompt_feedback'):
                        if response.prompt_feedback.block_reason:
                            raise ValueError(f"提示词被安全过滤拦截: {response.prompt_feedback.block_reason}")
                    raise ValueError(f"生成失败: {str(e)}")
            else:
                raise ValueError("对话历史的最后一条消息必须是用户角色")
        except Exception as e:
            error_msg = str(e)
            if "models/gemini-pro is not found" in error_msg:
                raise ValueError(f"找不到模型 '{self.model_name}'。请尝试更新模型名称，例如 'gemini-1.5-pro'。详细错误: {error_msg}")
            elif "API key not valid" in error_msg:
                raise ValueError(f"API密钥无效。请检查您的API密钥设置。详细错误: {error_msg}")
            else:
                raise ValueError(f"调用Gemini API时出错: {error_msg}")
    
    async def embed(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        获取文本的向量嵌入表示。
        
        Args:
            text: 需要嵌入的文本或文本列表
            
        Returns:
            文本的向量嵌入表示，单个文本返回一维向量，文本列表返回二维向量列表
        """
        try:
            # 尝试使用新版本的embedding模型
            embedding_model_name = "embedding-001"
            
            # 针对单个文本或文本列表处理
            if isinstance(text, str):
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: genai.embed_content(
                        model=embedding_model_name,
                        content=text
                    )
                )
                # 提取嵌入向量
                return result["embedding"]
            elif isinstance(text, list):
                # 对文本列表批量处理
                embeddings = []
                for item in text:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        lambda: genai.embed_content(
                            model=embedding_model_name, 
                            content=item
                        )
                    )
                    embeddings.append(result["embedding"])
                return embeddings
            else:
                raise TypeError("text参数必须是字符串或字符串列表")
        except Exception as e:
            error_msg = str(e)
            if "models/embedding-001 is not found" in error_msg:
                raise ValueError(f"找不到嵌入模型。详细错误: {error_msg}")
            elif "API key not valid" in error_msg:
                raise ValueError(f"API密钥无效。请检查您的API密钥设置。详细错误: {error_msg}")
            else:
                raise ValueError(f"获取嵌入表示时出错: {error_msg}") 