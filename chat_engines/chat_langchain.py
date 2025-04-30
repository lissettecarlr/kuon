"""
一个包含MCP和Memory Chat的聊天引擎。
用户可以选择是否使用MCP来增强对话能力。
"""

import os
import asyncio
from typing import Union, List, Dict, Any, Generator, Optional, AsyncGenerator

from loguru import logger
from .memory_chat_assistant import MemoryChatAssistant
from .openai_mcp_client import OpenAIMCPClient


class ChatEngine:
    """
    聊天引擎，整合MCP和Memory Chat功能
    
    如果用户选择使用MCP，则先调用MCP客户端获取结果，
    然后将结果和原本用户问题作为输入，传入Memory Chat。
    如果用户不使用MCP，则仅使用Memory Chat。
    """
    
    def __init__(self, 
                 mcp_config_path: str,
                 use_mcp: bool = False,
                 openai_api_key: Optional[str] = None,
                 openai_base_url: Optional[str] = None,
                 memory_model_name: str = "gpt-4.1",
                 chat_model_name: str = "gpt-4.1",
                 compress_interval: int = 600,
                 context_length_multiplier: float = 0.5,
                 max_long_term_memories: int = 1000,
                 use_tts_prompt: bool = False):
        """
        初始化聊天引擎
        
        Args:
            mcp_config_path: MCP服务器配置文件路径
            use_mcp: 是否使用MCP增强对话
            openai_api_key: OpenAI API密钥
            openai_base_url: OpenAI API基础URL
            memory_model_name: 记忆模型名称
            chat_model_name: 聊天模型名称
            compress_interval: 记忆压缩时间间隔（秒）
            context_length_multiplier: 上下文长度倍率
            max_long_term_memories: 长期记忆的最大条目数
            use_tts_prompt: 是否使用TTS提示词
        """
        # 初始化Memory Chat
        self.memory_chat = MemoryChatAssistant(
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url,
            memory_model_name=memory_model_name,
            chat_model_name=chat_model_name,
            compress_interval=compress_interval,
            context_length_multiplier=context_length_multiplier,
            max_long_term_memories=max_long_term_memories,
            use_tts_prompt=use_tts_prompt
        )
        
        # MCP设置
        self.use_mcp = use_mcp
        self.mcp_client = None
        self.mcp_config_path = mcp_config_path
        self.mcp_initialized = False
        
        # 如果使用MCP，记录日志
        logger.info(f"聊天引擎初始化完成，MCP功能: {'已启用' if use_mcp else '已禁用'}")
        
    async def initialize_mcp(self) -> None:
        """初始化MCP客户端"""
        if self.mcp_initialized:
            return
            
        try:
            self.mcp_client = OpenAIMCPClient(self.mcp_config_path)
            await self.mcp_client.initialize()
            self.mcp_initialized = True
            logger.debug("MCP客户端初始化成功")
        except Exception as e:
            logger.error(f"MCP客户端初始化失败: {str(e)}")
            self.mcp_client = None
            raise RuntimeError(f"MCP客户端初始化失败: {str(e)}")
    
    async def process_message(self, user_message: str) -> AsyncGenerator[str, None]:
        """
        处理用户消息
        
        Args:
            user_message: 用户消息
            
        Returns:
            异步生成器，用于流式返回助手回复
            
        Raises:
            RuntimeError: 当处理消息失败时
        """
        try:
            if self.use_mcp:
                # 确保MCP客户端已初始化
                if not self.mcp_initialized:
                    await self.initialize_mcp()
                
                # 首先使用MCP处理消息
                logger.debug("使用MCP处理消息")
                mcp_response = await self.mcp_client.process_message(user_message)
                
                # 如果MCP返回"无"，则不需要处理，直接传递原始消息给Memory Chat
                if mcp_response == "无":
                    logger.debug("MCP返回'无'，直接使用Memory Chat处理原始消息")
                    enhanced_message = user_message
                else:
                    # 否则，将MCP的结果与原始消息合并
                    logger.debug("将MCP结果与原始消息合并")
                    enhanced_message = f"""
                            已知工具获取信息：{mcp_response}
                            沟通消息：{user_message}
                    """             
                # 使用Memory Chat处理增强后的消息
                for chunk in self.memory_chat.chat(enhanced_message):
                    yield chunk
            else:
                # 直接使用Memory Chat
                logger.debug("直接使用Memory Chat处理消息")
                for chunk in self.memory_chat.chat(user_message):
                    yield chunk
                
        except Exception as e:
            error_message = f"处理消息时出错: {str(e)}"
            logger.error(error_message)
            # 在发生错误时，生成错误消息并退出生成器
            yield f"错误: {str(e)}"
            # 不抛出异常，而是返回，让异步生成器正常结束
            return
    
    async def cleanup(self) -> None:
        """清理资源"""
        self.memory_chat.exit()
        
        if self.mcp_client and self.mcp_initialized:
            await self.mcp_client.cleanup()
            self.mcp_initialized = False
    
    def clear_memory(self, clear_type: str = "all") -> None:
        """
        清除Memory Chat的记忆
        
        Args:
            clear_type: 清除类型，可以是'all'、'short_term'或'long_term'
        """
        self.memory_chat.clear_memory(clear_type)
