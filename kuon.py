import threading
import queue
from typing import List, Optional, Iterator, Union, Dict, Any
from loguru import logger
import yaml
import asyncio
from chat_engines import ChatEngine
from tts_engines import AliyunStreamEngine, TextToSpeechEngine
import sys

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO")

# 全局变量存储共享事件循环，避免多次创建和销毁
_global_event_loop = None

def get_event_loop():
    """获取全局事件循环"""
    global _global_event_loop
    if _global_event_loop is None:
        _global_event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_global_event_loop)
    return _global_event_loop

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
            if "tts" not in config:
                config["tts"] = {"enabled": False, "engine": "aliyun"}
            if "mcp" not in config:
                config["mcp"] = {"enabled": False, "config_path": ""}
                
            return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return {
            "tts": {"enabled": False, "engine": "aliyun"}, 
            "mcp": {"enabled": False, "config_path": ""}
        }

class AIAssistant: 
    def __init__(
        self,
        chat_engine: Optional[ChatEngine] = None,
        tts_engine: Optional[TextToSpeechEngine] = None,
    ):
        self.chat_engine = chat_engine
        self.tts_engine = tts_engine
        self.tts_input_queue = queue.Queue()
        
        # 处理响应的线程
        self.chat_thread_running = False # AI对话线程
        self.tts_thread_running = False # TTS线程
        self.tts_thread = None
        self.chat_thread = None
        
        # 保持MCP连接
        self.mcp_active = True
        
    def _tts_thread_function(self) -> None:
        """文本转语音的线程函数"""
        
        if self.tts_engine is None:
            logger.error("意外启动TTS线程")
            return
        
        self.tts_thread_running = True 
        while self.tts_thread_running:
            try:
                text = self.tts_input_queue.get(timeout=1)
                if text is None: 
                    break
             
                # 将文本转换为语音并播放
                self.tts_engine.text_to_speech(text)
                self.tts_input_queue.task_done()

            except queue.Empty:
                continue
        self.tts_engine.complete()
    
    def start_interactive_session(self) -> None:
        """开始交互式会话"""
        print("开始对话 (输入 'exit' 或 'quit' 退出)")
        
        if not self.chat_engine:
            print("错误: 聊天引擎未初始化")
            return
        
        while True:
            # 只接受文本输入
            try:
                text = input("\n你: ").strip()
                if not text:
                    continue
                    
                if text.lower() in ['exit', 'quit']:
                    # 确保在退出前停止所有线程
                    self.chat_thread_running = False
                    self.tts_thread_running = False
                    if self.tts_engine:
                        self.tts_engine.stop()
                    self.mcp_active = False  # 标记MCP可以关闭
                    break

                # 退出上一次的AI对话线程
                if self.chat_thread and self.chat_thread.is_alive():
                    logger.debug("退出上一次的AI对话线程")
                    self.chat_thread_running = False

                # 当新输入内容的时候，关闭线程，重置TTS
                if self.tts_thread and self.tts_thread.is_alive():
                    logger.debug("退出上一次的TTS线程")
                    self.tts_thread_running = False
                    if self.tts_engine:
                        self.tts_engine.stop()
                
                # 清空TTS队列
                while not self.tts_input_queue.empty():
                    try:
                        self.tts_input_queue.get_nowait()
                    except queue.Empty:
                        break
                
                # 使用 process_message 方法在线程中运行异步函数
                self.chat_thread = threading.Thread(
                    target=self._run_async_chat,
                    args=(text,)
                )
                self.chat_thread.start()

                # TTS线程
                ## 如果TTS引擎存在，则启动TTS线程
                if self.tts_engine is not None:
                    self.tts_engine.init()
                    self.tts_thread = threading.Thread(target=self._tts_thread_function)
                    self.tts_thread.start()
                
                # 等待AI回复完成
                self.chat_thread.join()
            except KeyboardInterrupt:
                print("\n输入被中断")
                continue
            except Exception as e:
                logger.error(f"处理用户输入时出错: {e}")
                print(f"\n处理输入时出错: {e}")
                continue
    
    def _run_async_chat(self, text: str) -> None:
        """在线程中运行异步聊天函数"""
        # 使用全局事件循环而不是每次创建新的循环
        loop = get_event_loop()
        
        async def stream_response():
            print("KUON: ", end="", flush=True)
            buffer = ""
            response_generator = None
            
            try:
                # 获取生成器但先不消费
                response_generator = self.chat_engine.process_message(text)
                
                async for chunk in response_generator:
                    if not self.chat_thread_running:
                        # 如果线程要求停止，但不要关闭生成器
                        break
                        
                    print(chunk, end="", flush=True)
                    buffer += chunk
                    
                    # 如果有TTS引擎，则将内容存入tts_input_queue
                    if self.tts_engine is not None:
                        separators = ["。", "！", "？", ".", "!", "?", "\n"]
                        for sep in separators:
                            if buffer.endswith(sep):
                                self.tts_input_queue.put(buffer)
                                buffer = ""
                
                # 如果缓冲区中还有内容，也推送到队列
                if buffer and self.tts_engine is not None:
                    self.tts_input_queue.put(buffer)
                
                # 标记响应结束
                if self.tts_engine is not None:
                    self.tts_input_queue.put(None)
                
                print()
            except Exception as e:
                logger.error(f"聊天过程中发生错误: {e}")
                print(f"\n聊天出错: {e}")
            
        try:
            # 运行异步函数
            self.chat_thread_running = True
            loop.run_until_complete(stream_response())
        except Exception as e:
            logger.error(f"运行异步聊天时出错: {e}")
            print(f"\n聊天出错: {e}")
    
    def exit(self) -> None:
        """退出并清理资源"""
        self.tts_thread_running = False
        self.chat_thread_running = False
        self.mcp_active = False  # 允许MCP关闭
        
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception as e:
                logger.debug(f"停止TTS引擎时出错: {e}")
        
        # 退出TTS引擎
        if hasattr(self.tts_engine, 'exit'):
            try:
                self.tts_engine.exit()
            except Exception as e:
                logger.debug(f"退出TTS引擎时出错: {e}")
        
        # 清理聊天引擎资源
        if self.chat_engine:
            try:
                # 使用全局事件循环清理资源
                loop = get_event_loop()
                loop.run_until_complete(self.chat_engine.cleanup())
            except Exception as e:
                logger.error(f"清理聊天引擎资源时出错: {e}")
        
        print("会话已结束")
        
        # 最后关闭全局事件循环
        global _global_event_loop
        if _global_event_loop:
            try:
                _global_event_loop.close()
                _global_event_loop = None
            except Exception as e:
                logger.error(f"关闭事件循环时出错: {e}")


async def initialize_chat_engine(config):
    """初始化聊天引擎"""
    try:
        tts_enabled = config.get("tts", {}).get("enabled", False)
        mcp_enabled = config.get("mcp", {}).get("enabled", False)
        mcp_config_path = config.get("mcp", {}).get("config_path", "")
        
        chat_engine = ChatEngine(
            mcp_config_path=mcp_config_path,
            use_mcp=mcp_enabled,
            use_tts_prompt=tts_enabled
        )
        
        # 只有在启用MCP时才初始化MCP
        if mcp_enabled:
            await chat_engine.initialize_mcp()
            
        return chat_engine
    except Exception as e:
        logger.error(f"初始化聊天引擎失败: {e}")
        raise


def main():
    try:
        config = load_config()

        # 使用全局事件循环初始化聊天引擎
        loop = get_event_loop()
        chat_engine = loop.run_until_complete(initialize_chat_engine(config))
        
        # 初始化TTS引擎
        tts_engine = None
        if config.get("tts", {}).get("enabled", False):
            engine_type = config.get("tts", {}).get("engine", "aliyun")
            if engine_type == "aliyun":
                tts_engine = AliyunStreamEngine()
            else:
                logger.warning(f"不支持的TTS引擎: {engine_type}")
        
        # 创建AI助手实例
        assistant = AIAssistant(
            chat_engine=chat_engine,
            tts_engine=tts_engine
        )
        
        try:
            assistant.start_interactive_session()
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        finally:
            assistant.exit()
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()

