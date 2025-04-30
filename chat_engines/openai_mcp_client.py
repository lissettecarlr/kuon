"""
mcp_client = OpenAIMCPClient("servers_config.json")
await mcp_client.initialize()
response = await mcp_client.process_message(user_input)
"""
import asyncio
import json
import os
import shutil
from contextlib import AsyncExitStack
from typing import Dict, Any, List

import httpx
from loguru import logger
from openai import AsyncOpenAI

from agents import (
    Agent,
    Runner,
    gen_trace_id,
    trace,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)
from agents.mcp import MCPServer, MCPServerStdio, MCPServerSse


class OpenAIMCPClient:
    def __init__(self, servers_config_path) :
        self.exit_stack = AsyncExitStack()
        self.mcp_servers: List[MCPServer] = []
        self.system_prompt = """
        你是一个工具调用单元，思考是否需要通使用工具。
        * 如果需要，则返回调用工具后的结果。
        * 如果不需要，则返回：无。
        """
        self.servers_config = self.load_server_config(servers_config_path)
        self._initialized = False
        self.model = "gpt-4.1"
        
    async def initialize(self) -> None:
        if self._initialized:
            return
        
        logger.info("开始初始化OpenAI MCP客户端")
  
        servers_start_time = asyncio.get_event_loop().time()
        self.mcp_servers = await self._init_mcp_servers(self.servers_config)
        servers_end_time = asyncio.get_event_loop().time()
        logger.info(f"MCP服务器列表初始化完成，耗时: {servers_end_time - servers_start_time:.2f}秒")
        

        self.agent = self._init_openai_agent(self.system_prompt, self.mcp_servers, self.model)
        self._initialized = True

    def load_server_config(self, file_path: str) -> Dict[str, Any]:
        """加载服务器配置"""
        with open(file_path, "r") as f:
            return json.load(f)

    def _init_openai_agent(self, system_prompt, mcp_servers, model: str = "gpt-4o"):
        """初始化OpenAI Agent"""
        client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            http_client=httpx.AsyncClient(verify=False),
        )
        
        set_default_openai_client(client=client, use_for_tracing=False)
        set_default_openai_api("chat_completions")
        set_tracing_disabled(disabled=True)

        agent = Agent(
            name="Assistant",
            instructions=system_prompt,
            mcp_servers=mcp_servers,
            model=model,
        )
        return agent

    async def _init_mcp_servers(self, servers_config: Dict[str, Any]) -> List[MCPServer]:
        """异步初始化MCP服务器并返回服务器列表"""
        mcp_servers = []
        for name, config in servers_config["mcpServers"].items():
            logger.debug(f"开始初始化服务器: {name}, 类型: {config['type']}")
            
            if config["type"] == "sse":
                logger.debug(f"初始化SSE服务器: {name}, URL: {config['url']}")
                server = MCPServerSse(
                    name=name,
                    params={
                        "url": config["url"],
                    }
                )
            else:
                command = shutil.which("npx") if config["command"] == "npx" else config["command"]
                if command is None:
                    raise ValueError("命令必须是有效的字符串，不能为None。")
                
                server = MCPServerStdio(
                    name=name,
                    params={
                        "command": command,
                        "args": config["args"],
                        "env": {**os.environ, **config["env"]} if config.get("env") else None,
                    }
                )
            
            connect_start = asyncio.get_event_loop().time()
            logger.debug(f"服务器 {name} 开始连接...")
            await self.exit_stack.enter_async_context(server)
            connect_end = asyncio.get_event_loop().time()
            logger.info(f"服务器 {name} 连接完成，耗时: {connect_end - connect_start:.2f}秒")
            
            mcp_servers.append(server)
   
        logger.info(f"所有 {len(mcp_servers)} 个MCP服务器初始化完成")
        return mcp_servers

    async def process_message(self, user_message: str) -> str:
        """处理用户消息并返回响应"""
        if not self._initialized:
            raise RuntimeError("MCP服务器未初始化，请先调用initialize方法")
            
        try:
            trace_id = gen_trace_id()
            with trace(workflow_name="User Query", trace_id=trace_id):
                logger.debug(f"处理用户消息: {user_message}")
                result = await Runner.run(starting_agent=self.agent, input=user_message)
                logger.debug(f"处理完成，获得响应")
                return result.final_output
                
        except Exception as e:
            error_msg = f"处理消息时出错: {str(e)}"
            logger.error(error_msg)
            # 发生错误时重置状态
            self._initialized = False
            self.mcp_servers = []
            self.agent = None
            return error_msg
    
    async def cleanup(self) -> None:
        """清理服务器资源"""
        if not self._initialized:
            return
            
        try:
            print("正在清理资源...")
            logger.info("开始清理所有服务器...")
            await self.exit_stack.aclose()
            logger.info("所有服务器清理完成")
        except Exception as e:
            logger.error(f"清理服务器资源时出错: {e}")
        finally:
            self._initialized = False
            self.mcp_servers = []
            self.agent = None 