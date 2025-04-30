"""
ChatEngine 示例
演示如何使用带有记忆和MCP工具调用功能的聊天引擎
"""

import os
import asyncio
import yaml
from dotenv import load_dotenv
from loguru import logger
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chat_engines import ChatEngine
load_dotenv()


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return {"mcp": {"enabled": True, "config_path": "mcp_server/temp_mcp_server.json"}}

config = load_config()
mcp_config = config.get("mcp", {})
mcp_enabled = mcp_config.get("enabled", True)
mcp_config_path = mcp_config.get("config_path", "mcp_server/temp_mcp_server.json")

logger.info(f"MCP配置: 启用={mcp_enabled}, 配置文件={mcp_config_path}")


async def interactive_chat():
    """交互式聊天示例"""
    print("\n" + "=" * 50)
    print("交互式聊天示例")
    print("=" * 50)
    print("输入'exit'或'退出'结束对话")
    
    chat_engine = ChatEngine(
        mcp_config_path=mcp_config_path,  # 从配置文件加载MCP配置路径
        use_mcp=mcp_enabled,              # 是否启用MCP
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_base_url=os.getenv("OPENAI_BASE_URL")
    )
    
    print(f"当前模式: {'使用MCP' if mcp_enabled else '不使用MCP'}")
    
    try:
        while True:
            user_input = input("\n用户: ")
            
            if user_input.lower() in ["exit", "退出", "q", "quit"]:
                print("谢谢使用，再见!")
                break
                
            print("AI: ", end="")
            try:
                async for chunk in chat_engine.process_message(user_input):
                    print(chunk, end="", flush=True)
                print()
            except Exception as e:
                print(f"\n对话出错: {e}")
    finally:
        await chat_engine.cleanup()

async def main():
    """主函数"""
    try:
        await interactive_chat()
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序异常: {e}") 